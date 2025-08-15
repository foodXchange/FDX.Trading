using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;

namespace FDX.Trading.TempModels;

public partial class FdxdbContext : DbContext
{
    public FdxdbContext()
    {
    }

    public FdxdbContext(DbContextOptions<FdxdbContext> options)
        : base(options)
    {
    }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        => optionsBuilder.UseSqlServer("Name=ConnectionStrings:DefaultConnection");

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
