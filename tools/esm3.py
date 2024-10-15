from typing import Literal, Annotated, List, Tuple

import os
import numpy as np
import torch
from esm.utils.structure.protein_chain import ProteinChain
from esm.sdk import client
from esm.sdk.api import (
    ESMProtein,
    GenerationConfig,
)

model = client(
    model="esm3-large-2024-03",
    # model="esm3-small-2024-03",
    url="https://forge.evolutionaryscale.ai",
    token=os.environ["ESM_KEY"],
)

Track = Literal["sequence", "structure"]

def pdb_lookup(pdb_id: str, chain_id: str) -> Tuple[str, List[List[List[float]]]]:
    if len(pdb_id) != 4:
        raise ValueError(f"Invalid PDB ID length: {len(pdb_id)}. Expected length is 4.")
    protein = ProteinChain.from_rcsb(pdb_id, chain_id)
    sequence = protein.sequence
    coordinates = protein.atom37_positions.tolist()
    return sequence, coordinates


def esm_generate(sequence_prompt: str, structure_prompt: List[List[List[float]]], 
                 track: Annotated[Track, "track"], num_decode_steps: int) -> Tuple[str, List[List[List[float]]]]:
    
    if len(sequence_prompt) != len(structure_prompt):
        raise ValueError(f"Invalid sequence_prompt length: {len(sequence_prompt)}. Expected length is {len(structure_prompt)}.")
        
    protein_prompt = ESMProtein(sequence=sequence_prompt, coordinates=torch.tensor(structure_prompt))

    sequence_generation_config = GenerationConfig(
        track=track,
        num_steps=num_decode_steps,
        temperature=0.5,  # We'll use a temperature of 0.5 to control the randomness of the decoding process
    )

    # Now, we can use the `generate` method of the model to decode the sequence
    generated_protein = model.generate(protein_prompt, sequence_generation_config)
    generated_protein.to_pdb("generated.pdb")
    return generated_protein.sequence, generated_protein.coordinates.tolist()

    