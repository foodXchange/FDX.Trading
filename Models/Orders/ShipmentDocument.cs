using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace FDX.Trading.Models.Orders;

[Table("ShipmentDocuments", Schema = "fdx")]
public class ShipmentDocument
{
    [Key]
    public Guid ShipmentDocumentId { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid ShipmentId { get; set; }
    
    [Required]
    [MaxLength(40)]
    public string DocType { get; set; } = string.Empty;
    // proforma_invoice/commercial_invoice/packing_list/coo/health_cert/kosher_cert/insurance/bl/awb
    
    [Required]
    [MaxLength(800)]
    public string BlobUri { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(300)]
    public string FileName { get; set; } = string.Empty;
    
    public Guid? UploadedBy { get; set; }
    
    public DateTimeOffset UploadedAt { get; set; } = DateTimeOffset.UtcNow;
    
    // Navigation properties
    [ForeignKey("ShipmentId")]
    public virtual Shipment Shipment { get; set; } = null!;
}