# USB Portability Architecture (UP - PORT)

## USB Storage Allocation (~8 GB Target)
- **RUDRA Runtime & Core Modules**: ~200 MB
- **Python Portable Environment**: ~150 MB
- **Local Embedded Models & Speech Data**: ~3 GB
- **Temporary Working Buffer / Caches**: ~1 GB
- **Logs & Audit Reports Storage**: ~500 MB
- **Reserved / Free Drive Space**: ~3.15 GB

## Key Considerations & Implementation Status
- **IMPLEMENTED**: Relative path management for all portable directories (`config/`, `data/`, `logs/`, `reports/`, `sessions/`) via `RUDRA_ROOT`.
- **IMPLEMENTED**: Storage capacity detection (`shutil.disk_usage`) and environment writability validation (`PortableRuntime.validate_environment()`).
- **SECURITY BOUNDARY**: No automated exploit autorun; explicit user initiation and session authorization required.
