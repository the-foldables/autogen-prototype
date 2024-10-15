from typing import Literal, Annotated

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

def pdb_lookup(pdb_id: str, chain_id: str) -> ProteinChain:
    if len(pdb_id) != 4:
        raise ValueError(f"Invalid PDB ID length: {len(pdb_id)}. Expected length is 4.")
    return ProteinChain.from_rcsb(pdb_id, chain_id)


def esm_generate(sequence_prompt: str, structure_prompt: torch.Tensor, 
                 track: Annotated[Track, "track"], num_decode_steps: int) -> ESMProtein:
    if len(sequence_prompt) != len(structure_prompt):
        raise ValueError(f"Invalid sequence_prompt length: {len(sequence_prompt)}. Expected length is {len(structure_prompt)}.")
        
    protein_prompt = ESMProtein(sequence=sequence_prompt, coordinates=structure_prompt)

    sequence_generation_config = GenerationConfig(
        track=track,
        num_steps=num_decode_steps,
        temperature=0.5,  # We'll use a temperature of 0.5 to control the randomness of the decoding process
    )

    # Now, we can use the `generate` method of the model to decode the sequence
    generated_protein = model.generate(protein_prompt, sequence_generation_config)
    return generated_protein

def save_protein(save_dir: str, generated_protein: ESMProtein):
    generated_protein.to_pdb(save_dir + "/generated.pdb")