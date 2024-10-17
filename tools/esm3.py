from typing import Literal, Annotated, List, Tuple, Union

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
    """
    Example command:
    pdb_lookup("1ITU","A")
    """
    if len(pdb_id) != 4:
        raise ValueError(f"Invalid PDB ID length: {len(pdb_id)}. Expected length is 4.")
    protein = ProteinChain.from_rcsb(pdb_id, chain_id)
    sequence = protein.sequence
    # coordinates = protein.atom37_positions.tolist()
    return sequence



def esm_generate(sequence_prompt: str, structure_prompt: List[List[List[Union[float, None]]]], 
                 track: Annotated[Track, "track"], num_decode_steps: int) -> Tuple[str, List[List[List[float]]]]:
    
    """
    Example command:
    esm_generate( '____', [[[None]*3]*37]*4, 'sequence', 2)
    """
    
    # enforce lengths
    if len(sequence_prompt) < len(structure_prompt):
        structure_prompt = structure_prompt[0:len(sequence_prompt)]
    else:
        sequence_prompt = sequence_prompt[0:len(structure_prompt)]

    # Switch None to np.nan
    structure_prompt = np.array(structure_prompt)
    structure_prompt[structure_prompt==None]=np.nan
    structure_prompt = structure_prompt.astype(float)

    protein_prompt = ESMProtein(sequence=sequence_prompt, coordinates=torch.tensor(structure_prompt))

    sequence_generation_config = GenerationConfig(
        track=track,
        num_steps=num_decode_steps,
        temperature=0.5,  # We'll use a temperature of 0.5 to control the randomness of the decoding process
    )

    # Now, we can use the `generate` method of the model to decode the sequence
    generated_protein = model.generate(protein_prompt, sequence_generation_config)
    generated_protein.to_pdb("generated.pdb")

    # coords = generated_protein.coordinates.numpy()
    # nan_coords = np.isnan(coords)
    # coords=coords.astype(object)
    # coords[nan_coords]=None
    # coords = coords.tolist()

    return generated_protein.sequence

    