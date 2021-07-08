import json
from watson_developer_cloud import VisualRecognitionV3
import cv2
import time
import random
import datetime
import requests
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from ibmcloudant.cloudant_v1 import CloudantV1
from ibmcloudant import CouchDbSessionAuthenticator
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator


# Constants for IBM COS values
COS_ENDPOINT = "https://s3.jp-tok.cloud-object-storage.appdomain.cloud" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "eJuMGEJg913QufpYpcw8H4yIlhWMfTA8IKbKwB2syTbQ" # eg "W00YixxxxxxxxxxMB-odB-2ySfTrFBIQQWanc--P3byk"
COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/68a32c0a4a824d6399a39e40e6a6ca31:faa157de-e615-452c-9015-98f3efbc9173::" # eg "crn:v1:bluemix:public:cloud-object-storage:global:a/3bf0d9003xxxxxxxxxx1c3e97696b71c:d6f04d83-6c4f-4a62-a165-696756d63903::"

# Create resource
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

authenticator = BasicAuthenticator('apikey-v2-cwvk9xyikq9rfuw4doizcx42evh315gtzr1fyt79030', '27adc4f4f6732de3c027a7d0a1c73eca')
service = CloudantV1(authenticator=authenticator)
service.set_service_url('https://apikey-v2-cwvk9xyikq9rfuw4doizcx42evh315gtzr1fyt79030:27adc4f4f6732de3c027a7d0a1c73eca@1da30996-6e6e-4416-b630-35d2537bdd3b-bluemix.cloudantnosqldb.appdomain.cloud')



def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))


def vis(image):
	visual_recognition = VisualRecognitionV3(
	    '2018-03-19',
	    iam_apikey='4iHUKBMoK4OTebxnZLrHOmfOHU2MRG5Im_b-OGUMuPMQ')

	with open('./'+image, 'rb') as images_file:
	    classes = visual_recognition.classify(
		images_file,
		threshold='0.6',
		classifier_ids='default').get_result()
	#print(classes)
	a=classes["images"][0]["classifiers"][0]["classes"]
	for i in a:
		#print(i["class"])
		if i["class"]=="animal":
			print("Animal Detected")
			return "animal"

bucket = "cropcmrec"
cam=cv2.VideoCapture('Horse.mp4')
while True:
	ret, frame=cam.read()
	gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	frame=cv2.resize(frame,(600,400))
	cv2.imwrite("image.jpg",frame)
	cv2.imshow("Final Image",frame)
	a=vis("image.jpg")
	if a=="animal":
		requests.get('https://www.fast2sms.com/dev/bulkV2?authorization=gNYhnkTEm37FPDp26SvbjrQ5ysUw9Cl0ecaABXduZH1Gx8ztqIhIXaYnVLO7ps1P8KvtiN9BCDHR5ruJ&route=q&message=Animal Deteted!&language=english&flash=0&numbers=')
		picname=datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
		cv2.imwrite(picname+'.jpg',frame)
		multi_part_upload('akhil', picname+'.jpg', picname+'.jpgjson_document={"link":COS_ENDPOINT+'/'+bucket+'/'+picname+'.jpg'}
                response = service.post_document(db="sample", document=json_document).get_result()
                print(response)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
    
client.disconnect()
cam.release()
cv2.destroyAllWindows()
