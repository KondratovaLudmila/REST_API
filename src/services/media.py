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
        """
        The avatar_upload function uploads an avatar image to Cloudinary, 
        and returns an uploaded CloudinaryImage object.
        
        :param self: Represent the instance of the class
        :param file: Upload the image to cloudinary
        :param public_id: Specify the public id of the image to be uploaded
        :return: A cloudinaryimage object
        :doc-author: Trelent
        """
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
        """
        The remove_media function is used to remove a media file from Cloudinary.
                
        
        :param self: Represent the instance of a class
        :param public_id: str: Specify the public id of the media to be removed
        :return: response object
        :doc-author: Trelent
        """
        result = destroy(public_id)
        
        return result
        



