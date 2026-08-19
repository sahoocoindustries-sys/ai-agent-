# USB Portability Architecture

## USB Storage Allocation (~8 GB Target)
- **RUDRA Runtime & Core Modules**: ~200 MB
- **Python Portable Environment**: ~150 MB
- **Local Embedded Models & Speech Data**: ~3 GB
- **Temporary Working Buffer / Caches**: ~1 GB
- **Logs & Audit Reports Storage**: ~500 MB
- **Reserved / Free Drive Space**: ~3.15 GB

## Key Considerations
- Read-heavy, write-minimized design to protect USB flash storage lifespan.
- Relative path management for all tools and configurations (`RUDRA_ROOT`).
- Respect target OS security: no automated exploit autorun; explicit user initiation.
