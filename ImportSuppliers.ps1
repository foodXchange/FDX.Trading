# PowerShell script to import suppliers directly to Azure SQL

$connectionString = "Server=fdx-sql-prod.database.windows.net;Database=fdxdb;User Id=fdxadmin;Password=FDX2030!;TrustServerCertificate=True;"
$csvPath = "C:\Users\fdxadmin\Downloads\Products 9_8_2025.csv"

# Import CSV
$products = Import-Csv $csvPath

# Get unique suppliers
$suppliers = $products | Where-Object { $_.Supplier -ne '' -and $_.Supplier -ne $null } | 
    Select-Object @{Name='Supplier';Expression={$_.Supplier}}, 
                  @{Name='Country';Expression={$_.'Supplier Country'}}, 
                  @{Name='Website';Expression={$_."Supplier's Website"}} -Unique

Write-Host "Found $($suppliers.Count) unique suppliers"

# Connect to database
$connection = New-Object System.Data.SqlClient.SqlConnection
$connection.ConnectionString = $connectionString
$connection.Open()

$suppliersCreated = 0
$productsCreated = 0

foreach ($supplier in $suppliers) {
    $supplierName = if ($supplier.Supplier -match '^([^,]+)') { $matches[1].Trim() } else { $supplier.Supplier }
    $username = $supplierName.ToLower() -replace ' ', '_' -replace '[^a-z0-9_]', ''
    if ($username.Length -gt 50) { $username = $username.Substring(0, 50) }
    
    # Check if supplier already exists
    $checkCmd = $connection.CreateCommand()
    $checkCmd.CommandText = "SELECT COUNT(*) FROM FdxUsers WHERE Username = @username"
    $checkCmd.Parameters.AddWithValue("@username", $username)
    $exists = $checkCmd.ExecuteScalar()
    
    if ($exists -eq 0) {
        # Insert supplier user
        $insertCmd = $connection.CreateCommand()
        $insertCmd.CommandText = @"
INSERT INTO FdxUsers (Username, Password, Email, CompanyName, Type, Country, Website, 
    IsActive, RequiresPasswordChange, DataComplete, Verification, CreatedAt, ImportedAt,
    PhoneNumber, Address, Category, BusinessType, FullDescription, SubCategories)
VALUES (@username, 'FDX2025!', @email, @companyName, 3, @country, @website,
    1, 1, 0, 1, GETDATE(), GETDATE(), '', '', '', '', '', '')
"@
        $insertCmd.Parameters.AddWithValue("@username", $username)
        $insertCmd.Parameters.AddWithValue("@email", "$username@supplier.fdx")
        $insertCmd.Parameters.AddWithValue("@companyName", $supplierName)
        $country = if ($supplier.Country) { $supplier.Country } else { "" }
        $website = if ($supplier.Website) { $supplier.Website } else { "" }
        $insertCmd.Parameters.AddWithValue("@country", $country)
        $insertCmd.Parameters.AddWithValue("@website", $website)
        
        try {
            $insertCmd.ExecuteNonQuery()
            $suppliersCreated++
            Write-Host "Created supplier: $supplierName"
        } catch {
            Write-Host "Error creating supplier $supplierName : $_"
        }
    }
}

# Import products (simplified - just create unique products)
$uniqueProducts = $products | Where-Object { $_.'Product code' -ne '' -and $_.'Product code' -ne $null } | 
    Select-Object 'Product code', 'Product Name', 'Products Category & Family' -Unique

foreach ($product in $uniqueProducts) {
    $productCode = $product.'Product code'.Trim()
    
    # Check if product already exists
    $checkCmd = $connection.CreateCommand()
    $checkCmd.CommandText = "SELECT COUNT(*) FROM Products WHERE ProductCode = @code"
    $checkCmd.Parameters.AddWithValue("@code", $productCode)
    $exists = $checkCmd.ExecuteScalar()
    
    if ($exists -eq 0) {
        $category = if ($product.'Products Category & Family') { 
            ($product.'Products Category & Family' -split ',')[0].Trim() 
        } else { "" }
        
        $insertCmd = $connection.CreateCommand()
        $insertCmd.CommandText = @"
INSERT INTO Products (ProductCode, ProductName, Category, Status, CreatedAt, ImportedAt)
VALUES (@code, @name, @category, 0, GETDATE(), GETDATE())
"@
        $insertCmd.Parameters.AddWithValue("@code", $productCode)
        $productName = if ($product.'Product Name') { $product.'Product Name' } else { $productCode }
        $insertCmd.Parameters.AddWithValue("@name", $productName)
        $insertCmd.Parameters.AddWithValue("@category", $category)
        
        try {
            $insertCmd.ExecuteNonQuery()
            $productsCreated++
            if ($productsCreated % 10 -eq 0) {
                Write-Host "Created $productsCreated products..."
            }
        } catch {
            Write-Host "Error creating product $productCode : $_"
        }
    }
}

$connection.Close()

Write-Host "`n========== Import Summary =========="
Write-Host "Suppliers created: $suppliersCreated"
Write-Host "Products created: $productsCreated"
Write-Host "Total suppliers in system: $($suppliers.Count)"
Write-Host "====================================`n"