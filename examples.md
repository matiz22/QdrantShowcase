# Qdrant CLI Example Commands

Here are some example commands for using the Qdrant CLI tool:

## Connection Options

All commands support these connection options:
```bash
--url HOSTNAME    # Qdrant server URL (default: localhost)
--port PORT       # Qdrant server port (default: 6333)
--api-key KEY     # API key for authentication (if needed)
```

## Collection Management

### Create a new collection
```bash
# Create a collection with default settings (vector size 1536, Cosine distance)
python main.py create-collection my_collection

# Create a collection with custom settings
python main.py create-collection my_custom_collection --vector-size 768 --distance Euclid
```

### List all collections
```bash
python main.py list-collections
```

### Delete a collection
```bash
python main.py delete-collection my_collection
```

## Working with Points

### Add points

Add a point using text (which will be embedded with OpenAI):
```bash
python main.py add-point my_collection point_id1 --text "This is a sample text that will be embedded"
```

Add a point with metadata:
```bash
python main.py add-point my_collection point_id2 --text "Another sample text" --payload '{"category": "example", "importance": 5}'
```

Add a point with a raw vector (if you already have embeddings):
```bash
python main.py add-point my_collection point_id3 --vector '[0.1, 0.2, 0.3, ...]' --payload '{"source": "external"}'
```

### Add all markdown files from a directory

Process and add all markdown files from a directory:
```bash
# Default usage (uses UUID for IDs to avoid format errors)
python main.py add-markdown-files my_collection /path/to/markdown/files

# Use numeric IDs generated from filenames
python main.py add-markdown-files my_collection /path/to/markdown/files --numeric-ids
```

This command will:
1. Scan the directory for all `.md` files
2. Generate embeddings for each file's content
3. Store each file in the collection with:
   - ID: UUID (by default) or numeric ID (with --numeric-ids)
   - Vector: embedding of the file content
   - Payload: includes the original filename and path

### Search for similar points

Search using text (which will be embedded):
```bash
python main.py search my_collection --text "Find something similar to this"
```

Search with limited results:
```bash
python main.py search my_collection --text "Find top matches" --limit 5
```

Search with a raw vector:
```bash
python main.py search my_collection --vector '[0.1, 0.2, 0.3, ...]' --limit 3
```

### Delete points
```bash
python main.py delete-point my_collection point_id1
```

## Examples with Remote Qdrant Server

Connect to a remote Qdrant server:
```bash
python main.py --url api.qdrant.example.com --port 6333 --api-key YOUR_API_KEY list-collections
```

Add a point to a collection on a remote server:
```bash
python main.py --url api.qdrant.example.com --api-key YOUR_API_KEY add-point my_collection remote_point1 --text "Text to be stored on remote server"
```

Process all markdown files and add them to a collection on a remote server:
```bash
python main.py --url api.qdrant.example.com --api-key YOUR_API_KEY add-markdown-files my_collection /path/to/docs
```
