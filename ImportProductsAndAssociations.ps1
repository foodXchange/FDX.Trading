# PowerShell script to import products and create supplier-product associations
# This script assumes suppliers are already created (which they are)

$connectionString = "Server=fdx-sql-prod.database.windows.net;Database=fdxdb;User Id=fdxadmin;Password=FDX2030!;TrustServerCertificate=True;"
$csvPath = "C:\Users\fdxadmin\Downloads\Products 9_8_2025.csv"

# Import CSV
$products = Import-Csv $csvPath

Write-Host "Starting product and association import..."
Write-Host "CSV contains $($products.Count) rows"

# Connect to database
$connection = New-Object System.Data.SqlClient.SqlConnection
$connection.ConnectionString = $connectionString
$connection.Open()

# First, create all unique products
$uniqueProducts = $products | Where-Object { $_.'Product code' -ne '' -and $_.'Product code' -ne $null } | 
    Select-Object 'Product code', 'Product Name', 'Products Category & Family' -Unique

Write-Host "`nFound $($uniqueProducts.Count) unique products"

$productsCreated = 0
$productIdMap = @{}

foreach ($product in $uniqueProducts) {
    $productCode = $product.'Product code'.Trim()
    
    # Check if product already exists
    $checkCmd = $connection.CreateCommand()
    $checkCmd.CommandText = "SELECT Id FROM Products WHERE ProductCode = @code"
    $checkCmd.Parameters.AddWithValue("@code", $productCode)
    $existingId = $checkCmd.ExecuteScalar()
    
    if ($existingId -eq $null) {
        $category = if ($product.'Products Category & Family') { 
            ($product.'Products Category & Family' -split ',')[0].Trim() 
        } else { "" }
        
        $insertCmd = $connection.CreateCommand()
        $insertCmd.CommandText = @"
INSERT INTO Products (ProductCode, ProductName, Category, Status, IsKosher, IsOrganic, IsVegan, IsGlutenFree, CreatedAt, ImportedAt)
OUTPUT INSERTED.Id
VALUES (@code, @name, @category, 0, 0, 0, 0, 0, GETDATE(), GETDATE())
"@
        $insertCmd.Parameters.AddWithValue("@code", $productCode)
        $productName = if ($product.'Product Name') { $product.'Product Name' } else { $productCode }
        $insertCmd.Parameters.AddWithValue("@name", $productName)
        $insertCmd.Parameters.AddWithValue("@category", $category)
        
        try {
            $newId = $insertCmd.ExecuteScalar()
            $productIdMap[$productCode] = $newId
            $productsCreated++
            if ($productsCreated % 10 -eq 0) {
                Write-Host "Created $productsCreated products..."
            }
        } catch {
            Write-Host "Error creating product $productCode : $_"
        }
    } else {
        $productIdMap[$productCode] = $existingId
    }
}

Write-Host "Products created: $productsCreated"

# Now create SupplierDetails for each supplier and associate products
Write-Host "`nCreating supplier details and product associations..."

$supplierDetailsCreated = 0
$associationsCreated = 0
$supplierIdMap = @{}

# Get unique suppliers from CSV
$uniqueSuppliers = $products | Where-Object { $_.Supplier -ne '' -and $_.Supplier -ne $null } | 
    Select-Object Supplier -Unique

foreach ($supplier in $uniqueSuppliers) {
    $supplierName = if ($supplier.Supplier -match '^([^,]+)') { $matches[1].Trim() } else { $supplier.Supplier }
    $username = $supplierName.ToLower() -replace ' ', '_' -replace '[^a-z0-9_]', ''
    if ($username.Length -gt 50) { $username = $username.Substring(0, 50) }
    
    # Get user ID for this supplier
    $getUserCmd = $connection.CreateCommand()
    $getUserCmd.CommandText = "SELECT Id FROM FdxUsers WHERE Username = @username AND Type = 3"
    $getUserCmd.Parameters.AddWithValue("@username", $username)
    $userId = $getUserCmd.ExecuteScalar()
    
    if ($userId -ne $null) {
        # Check if SupplierDetails already exists
        $checkDetailsCmd = $connection.CreateCommand()
        $checkDetailsCmd.CommandText = "SELECT Id FROM SupplierDetails WHERE UserId = @userId"
        $checkDetailsCmd.Parameters.AddWithValue("@userId", $userId)
        $supplierDetailsId = $checkDetailsCmd.ExecuteScalar()
        
        if ($supplierDetailsId -eq $null) {
            # Create SupplierDetails record
            $insertDetailsCmd = $connection.CreateCommand()
            $insertDetailsCmd.CommandText = @"
INSERT INTO SupplierDetails (UserId, Description, ProductCategories, IsVerified, CreatedAt, UpdatedAt)
OUTPUT INSERTED.Id
VALUES (@userId, @desc, @categories, 1, GETDATE(), GETDATE())
"@
            $insertDetailsCmd.Parameters.AddWithValue("@userId", $userId)
            $insertDetailsCmd.Parameters.AddWithValue("@desc", "Supplier imported from CSV")
            
            # Get categories from their products
            $supplierProducts = $products | Where-Object { $_.Supplier -eq $supplier.Supplier }
            $categories = ($supplierProducts | Select-Object -ExpandProperty 'Products Category & Family' -Unique | Where-Object { $_ -ne '' }) -join ', '
            if ($categories.Length -gt 200) { $categories = $categories.Substring(0, 200) }
            $insertDetailsCmd.Parameters.AddWithValue("@categories", $categories)
            
            try {
                $supplierDetailsId = $insertDetailsCmd.ExecuteScalar()
                $supplierDetailsCreated++
                Write-Host "Created supplier details for: $supplierName"
            } catch {
                Write-Host "Error creating supplier details for $supplierName : $_"
                continue
            }
        }
        
        $supplierIdMap[$supplier.Supplier] = $supplierDetailsId
    }
}

Write-Host "Supplier details created: $supplierDetailsCreated"

# Now create supplier-product associations
Write-Host "`nCreating supplier-product associations..."

foreach ($row in $products) {
    if ($row.Supplier -eq '' -or $row.Supplier -eq $null -or $_.'Product code' -eq '' -or $_.'Product code' -eq $null) {
        continue
    }
    
    $supplierDetailsId = $supplierIdMap[$row.Supplier]
    $productId = $productIdMap[$row.'Product code'.Trim()]
    
    if ($supplierDetailsId -ne $null -and $productId -ne $null) {
        # Check if association already exists
        $checkAssocCmd = $connection.CreateCommand()
        $checkAssocCmd.CommandText = "SELECT COUNT(*) FROM SupplierProducts WHERE SupplierDetailsId = @sid AND ProductId = @pid"
        $checkAssocCmd.Parameters.AddWithValue("@sid", $supplierDetailsId)
        $checkAssocCmd.Parameters.AddWithValue("@pid", $productId)
        $exists = $checkAssocCmd.ExecuteScalar()
        
        if ($exists -eq 0) {
            $insertAssocCmd = $connection.CreateCommand()
            $insertAssocCmd.CommandText = @"
INSERT INTO SupplierProducts (SupplierDetailsId, ProductId, Status, CreatedAt, UpdatedAt)
VALUES (@sid, @pid, 0, GETDATE(), GETDATE())
"@
            $insertAssocCmd.Parameters.AddWithValue("@sid", $supplierDetailsId)
            $insertAssocCmd.Parameters.AddWithValue("@pid", $productId)
            
            try {
                $insertAssocCmd.ExecuteNonQuery()
                $associationsCreated++
                if ($associationsCreated % 50 -eq 0) {
                    Write-Host "Created $associationsCreated associations..."
                }
            } catch {
                # Silently continue on duplicate key errors
            }
        }
    }
}

$connection.Close()

Write-Host "`n========== Import Summary =========="
Write-Host "Products created: $productsCreated"
Write-Host "Supplier details created: $supplierDetailsCreated"
Write-Host "Product associations created: $associationsCreated"
Write-Host "===================================="