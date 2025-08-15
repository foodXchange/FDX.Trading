-- Check Request and RequestItem data in FDX database
-- Run this in Azure Data Studio or SSMS connected to fdxdb

-- Summary counts
SELECT 'Requests' as TableName, COUNT(*) as RecordCount FROM Requests
UNION ALL
SELECT 'RequestItems', COUNT(*) FROM RequestItems
UNION ALL
SELECT 'RequestItemImages', COUNT(*) FROM RequestItemImages;

-- Sample Request data
SELECT TOP 5 
    r.Id,
    r.RequestNumber,
    r.Title,
    r.BuyerName,
    r.BuyerCompany,
    r.Status,
    r.CreatedAt,
    (SELECT COUNT(*) FROM RequestItems WHERE RequestId = r.Id) as ItemCount
FROM Requests r
ORDER BY r.CreatedAt DESC;

-- Sample RequestItem data
SELECT TOP 10
    ri.Id,
    ri.RequestId,
    r.RequestNumber,
    ri.ProductName,
    ri.BenchmarkBrand,
    ri.Quantity,
    ri.Unit,
    ri.TargetPrice
FROM RequestItems ri
INNER JOIN Requests r ON ri.RequestId = r.Id
ORDER BY ri.CreatedAt DESC;

-- Request status distribution
SELECT 
    CASE Status 
        WHEN 0 THEN 'Draft'
        WHEN 1 THEN 'Active'
        WHEN 2 THEN 'Closed'
        ELSE 'Unknown'
    END as Status,
    COUNT(*) as Count
FROM Requests
GROUP BY Status;

-- Requests with Kosher/FreeFrom requirements
SELECT 
    COUNT(CASE WHEN IsKosher = 1 THEN 1 END) as KosherRequests,
    COUNT(CASE WHEN IsFreeFrom = 1 THEN 1 END) as FreeFromRequests,
    COUNT(*) as TotalRequests
FROM Requests;

-- Most requested products
SELECT TOP 10
    ProductName,
    COUNT(*) as RequestCount,
    AVG(Quantity) as AvgQuantity,
    MIN(TargetPrice) as MinPrice,
    MAX(TargetPrice) as MaxPrice
FROM RequestItems
GROUP BY ProductName
ORDER BY RequestCount DESC;