import os
import argparse
import json
import glob
import re
import uuid
from typing import List, Optional
from pathlib import Path

from dotenv import load_dotenv

from vector import get_openai_embedding
from qdrant import QdrantDB

def create_collection_command(args):
    client = QdrantDB(url=args.url, port=args.port, api_key=args.api_key)
    success = client.create_collection(
        collection_name=args.collection_name,
        vector_size=args.vector_size,
        distance=args.distance
    )
    if success:
        print(f"Collection '{args.collection_name}' created successfully")
    else:
        print(f"Failed to create collection '{args.collection_name}'")

def list_collections_command(args):
    client = QdrantDB(url=args.url, port=args.port, api_key=args.api_key)
    collections = client.list_collections()
    print("Available collections:")
    for collection in collections:
        print(f"- {collection.name}")

def add_point_command(args):
    client = QdrantDB(url=args.url, port=args.port, api_key=args.api_key)
    
    # Get embedding if text is provided
    if args.text:
        vector = get_openai_embedding(args.text)
    else:
        try:
            vector = json.loads(args.vector)
        except:
            print("Error: Vector must be a valid JSON array of floats")
            return
    
    # Parse payload if provided
    payload = None
    if args.payload:
        try:
            payload = json.loads(args.payload)
        except:
            print("Error: Payload must be a valid JSON object")
            return
    
    success = client.add_point(
        collection_name=args.collection_name,
        id=args.id,
        vector=vector,
        payload=payload
    )
    
    if success:
        print(f"Point added to collection '{args.collection_name}' with ID {args.id}")
    else:
        print(f"Failed to add point to collection '{args.collection_name}'")

def search_command(args):
    client = QdrantDB(url=args.url, port=args.port, api_key=args.api_key)
    
    # Get embedding if text is provided
    if args.text:
        vector = get_openai_embedding(args.text)
    else:
        try:
            vector = json.loads(args.vector)
        except:
            print("Error: Vector must be a valid JSON array of floats")
            return
    
    results = client.search(
        collection_name=args.collection_name,
        query_vector=vector,
        limit=args.limit
    )
    
    print(f"Search results from '{args.collection_name}':")
    for result in results:
        print(f"ID: {result.id}, Score: {result.score}")
        if hasattr(result, 'payload') and result.payload:
            print(f"Payload: {result.payload}")
        print("---")

def delete_point_command(args):
    client = QdrantDB(url=args.url, port=args.port, api_key=args.api_key)
    success = client.delete_points(
        collection_name=args.collection_name,
        ids=[args.id]
    )
    if success:
        print(f"Point with ID {args.id} deleted from collection '{args.collection_name}'")
    else:
        print(f"Failed to delete point with ID {args.id}")

def delete_collection_command(args):
    client = QdrantDB(url=args.url, port=args.port, api_key=args.api_key)
    success = client.delete_collection(args.collection_name)
    if success:
        print(f"Collection '{args.collection_name}' deleted successfully")
    else:
        print(f"Failed to delete collection '{args.collection_name}'")

def add_markdown_files_command(args):
    """
    Process all markdown files in a directory and add them to Qdrant.
    The filename is stored in the payload.
    """
    client = QdrantDB(url=args.url, port=args.port, api_key=args.api_key)
    
    # Find all markdown files in the specified path
    markdown_files = glob.glob(os.path.join(args.directory_path, "*.md"))
    
    if not markdown_files:
        print(f"No markdown files found in {args.directory_path}")
        return
    
    print(f"Found {len(markdown_files)} markdown files")
    
    # Process each file
    for file_path in markdown_files:
        try:
            # Get the filename for the payload
            filename = os.path.basename(file_path)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Generate embedding
            vector = get_openai_embedding(content)
            
            # Create a payload with the filename
            payload = {
                "filename": filename,
                "source_path": file_path
            }
            
            # Generate valid ID based on options
            if args.numeric_ids:
                # Use a simple hash for numeric IDs
                file_id = abs(hash(filename)) % (2**63 - 1)
                print(f"Using numeric ID: {file_id} for file: {filename}")
            else:
                # Default to UUID (most reliable option)
                file_id = str(uuid.uuid4())
                print(f"Using UUID: {file_id} for file: {filename}")
            
            # Add to Qdrant
            success = client.add_point(
                collection_name=args.collection_name,
                id=file_id,
                vector=vector,
                payload=payload
            )
            
            if success:
                print(f"Added file '{filename}' to collection '{args.collection_name}' with ID '{file_id}'")
            else:
                print(f"Failed to add file '{filename}'")
                
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

def setup_argparse():
    parser = argparse.ArgumentParser(description='Qdrant Vector Database CLI')
    parser.add_argument('--url', default='localhost', help='Qdrant server URL')
    parser.add_argument('--port', type=int, default=6333, help='Qdrant server port')
    parser.add_argument('--api-key', help='Qdrant API key')
    
    subparsers = parser.add_subparsers(title='commands', dest='command')
    
    # Create collection command
    create_parser = subparsers.add_parser('create-collection', help='Create a new collection')
    create_parser.add_argument('collection_name', help='Name of the collection')
    create_parser.add_argument('--vector-size', type=int, default=3072, help='Size of vectors')
    create_parser.add_argument('--distance', default='Cosine', choices=['Cosine', 'Euclid', 'Dot'], 
                              help='Distance metric')
    create_parser.set_defaults(func=create_collection_command)
    
    # List collections command
    list_parser = subparsers.add_parser('list-collections', help='List all collections')
    list_parser.set_defaults(func=list_collections_command)
    
    # Add point command
    add_parser = subparsers.add_parser('add-point', help='Add a point to a collection')
    add_parser.add_argument('collection_name', help='Name of the collection')
    add_parser.add_argument('id', help='ID for the point')
    add_point_group = add_parser.add_mutually_exclusive_group(required=True)
    add_point_group.add_argument('--text', help='Text to embed using OpenAI')
    add_point_group.add_argument('--vector', help='Vector as JSON array')
    add_parser.add_argument('--payload', help='Optional payload as JSON')
    add_parser.set_defaults(func=add_point_command)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for similar vectors')
    search_parser.add_argument('collection_name', help='Name of the collection')
    search_point_group = search_parser.add_mutually_exclusive_group(required=True)
    search_point_group.add_argument('--text', help='Text to embed using OpenAI')
    search_point_group.add_argument('--vector', help='Vector as JSON array')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum number of results')
    search_parser.set_defaults(func=search_command)
    
    # Delete point command
    delete_point_parser = subparsers.add_parser('delete-point', help='Delete a point')
    delete_point_parser.add_argument('collection_name', help='Name of the collection')
    delete_point_parser.add_argument('id', help='ID of the point to delete')
    delete_point_parser.set_defaults(func=delete_point_command)
    
    # Delete collection command
    delete_coll_parser = subparsers.add_parser('delete-collection', help='Delete a collection')
    delete_coll_parser.add_argument('collection_name', help='Name of the collection')
    delete_coll_parser.set_defaults(func=delete_collection_command)
    
    # Add markdown files command
    add_md_parser = subparsers.add_parser('add-markdown-files', help='Add all markdown files from a directory')
    add_md_parser.add_argument('collection_name', help='Name of the collection')
    add_md_parser.add_argument('directory_path', help='Path to directory containing markdown files')
    add_md_parser.add_argument('--numeric-ids', action='store_true', 
                               help='Use numeric IDs instead of UUIDs (default is UUID)')
    add_md_parser.set_defaults(func=add_markdown_files_command)
    
    return parser

if __name__ == "__main__":
    load_dotenv()

    parser = setup_argparse()
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
