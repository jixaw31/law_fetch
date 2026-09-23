from typing import List

def dynamic_batch_texts(list_of_dicts, tokenizer, max_length: int = 65530) -> List[List[dict]]:
    """
    Dynamically batch texts based on token length limits.
    
    Args:
        texts: List of input strings
        tokenizer_path: Path to tokenizer.json file
        max_length: Maximum token length per batch (default: 8192)
    
    Returns:
        List of batches, where each batch is a list of strings
    """

    
    to_embed_list = [x['embedding_text'] for x in list_of_dicts]
    
    encodings = tokenizer.encode_batch(to_embed_list)
    for i, x in enumerate(list_of_dicts):
        x["len_encoding"] = len(encodings[i].ids)
    

    sorted_list_of_dicts = sorted(list_of_dicts, key=lambda x: x['len_encoding'], reverse=True)

    # TODO NEED TO PERHAPS CHUNKIFIY THESE HEAVY WEIGHTS.
    
    # Create batches
    batches = []
    current_batch = []
    current_token_count = 0

    for item in sorted_list_of_dicts:
        # If a single text exceeds max_length, handle it separately
        if item['len_encoding'] > max_length:
            # If we have accumulated texts, save the current batch first
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_token_count = 0
            
            # Put the long text in its own batch (truncation will happen later)
            batches.append([item])
            continue
        
        # If adding this text exceeds limit, start new batch
        if current_batch and current_token_count + item['len_encoding'] > max_length:
            batches.append(current_batch)
            current_batch = [item]
            current_token_count = item['len_encoding'] 
        else:
            current_batch.append(item)
            current_token_count += item['len_encoding'] 

    # Add final batch
    if current_batch:
        batches.append(current_batch)

    return batches

if __name__ == "__main__":
    pass