$csv = Import-Csv 'C:\Users\fdxadmin\Downloads\Products 9_8_2025.csv'
$suppliers = $csv | Where-Object { $_.Supplier -ne '' -and $_.Supplier -ne $null } | 
    Select-Object Supplier, @{Name='Country';Expression={$_.'Supplier Country'}}, @{Name='Website';Expression={$_."Supplier's Website"}} -Unique

$suppliers | ForEach-Object {
    Write-Host "Supplier: $($_.Supplier), Country: $($_.Country), Website: $($_.Website)"
}

Write-Host "`nTotal unique suppliers: $($suppliers.Count)"