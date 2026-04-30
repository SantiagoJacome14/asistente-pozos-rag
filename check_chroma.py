import chromadb
print('chromadb version:', chromadb.__version__)
print('has PersistentClient:', hasattr(chromadb, 'PersistentClient'))
print('has Client:', hasattr(chromadb, 'Client'))
print('dir contains:', [name for name in dir(chromadb) if 'Client' in name or 'Persistent' in name])
