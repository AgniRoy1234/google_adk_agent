from google.genai import types
from google.adk.tools import ToolContext 
import logging


async def save_content_as_artifact(
    filename: str, 
    content_bytes: bytes, 
    mime_type: str, 
    tool_context: ToolContext
) -> dict:
    """
    Accepts raw content bytes and a MIME type, packages it into a GenAI Part object,
    and saves it to the ADK system as a versioned artifact.
    """
    # --- STEP 1: Wrap binary data into a Part object ---
    artifact_part = types.Part.from_bytes(
        data=content_bytes, 
        mime_type=mime_type
    )
    
    # --- STEP 2: Save the Artifact to the ADK System ---
    # save_artifact handles versioning and makes the file available for download.
    version = await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part
    ) 

    logging.info(f"Saved artifact '{filename}' as version {version}.")
    
    # --- STEP 3: Return success metadata ---
    return {
        "status": "success",
        "filename": filename,
        "version": version,
        "message": f"Successfully saved '{filename}' as version {version}."
    }