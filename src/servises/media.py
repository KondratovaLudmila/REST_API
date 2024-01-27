import cloudinary
from cloudinary.uploader import upload_image, destroy
from cloudinary import CloudinaryImage


from src.conf.config import settings


cloudinary.config( 
  cloud_name = settings.cloudinary.cloud_name, 
  api_key = settings.cloudinary.api_key, 
  api_secret = settings.cloudinary.api_secret
)

DEFAULT_TAG = "avatar"

class MediaCloud:
    FOLDER = settings.cloudinary.folder

    async def avatar_upload(self, file, public_id=None) -> CloudinaryImage:
        options = {
                    "overwrite": True,
                    "width": 300,
                    "crop": "thumb", 
                    "gravity": "faces",
                    "format": "jpeg",
                    }
        
        if public_id:
            options.update({"public_id": public_id})
        else:
            options.update({"folder": self.FOLDER + "/avatar"})
        
        image = upload_image(file, **options)
        
        return image
    
    async def remove_media(self, public_id: str):
        result = destroy(public_id)
        
        return result
        



