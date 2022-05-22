import torch
import clip
from PIL import Image
import os
import time
from utils import getTime, o, waitForFileExist
from videoLoader import convertToTs, cutVideo, getVideoFrames, mergeVideo


class SearchModel():
    image_embeddings: list = None
    def __init__(self) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=self.device)
        self.model = model
        self.preprocess = preprocess

    def getPreprocessImages(self, image_paths: list = [], video_frames = None):
        if video_frames:
            return [self.preprocess(Image.fromarray(img)).unsqueeze(0).to(self.device) for img in video_frames]
        return [self.preprocess(Image.open(img)).unsqueeze(0).to(self.device) for img in image_paths]

    def getRange(self, maxIndex: int, result: list, thod = 0.1):
        maxImageScore = result[maxIndex]["score"]
        leftIndex = maxIndex
        rightIndex = maxIndex
        for i in range(maxIndex-1):
            prev_index = maxIndex - 1 - i
            if result[prev_index]["score"] >= maxImageScore - thod:
                leftIndex = prev_index
            else:
                break

        for i in range(maxIndex+1, len(result)):
            if result[i]["score"] >= maxImageScore - thod:
                rightIndex = i
            else:
                break
        return leftIndex, rightIndex

    def getTextTokenize(self, t: str):
        return clip.tokenize([t, "unknown"]).to(self.device)

    def newSearchInImages(self, t: str, images):
        result = []
        maxImage = {
            "index": 0,
            "score": 0
        }
        with torch.no_grad():
            t0 = time.time()
            images_features = [self.model.encode_image(img) for img in images] if self.image_embeddings is None else self.image_embeddings
            if self.image_embeddings is None:
                self.image_embeddings = images_features
            text_features = self.model.encode_text(self.getTextTokenize(t))

            logit_scale = self.model.logit_scale.exp()
            t1 = time.time()
            print(t1 - t0, 's')
                
            for i, imgObj in enumerate(images_features):
                image_features = imgObj
                # normalized features
                image_features = image_features / image_features.norm(dim=1, keepdim=True)
                text_features = text_features / text_features.norm(dim=1, keepdim=True)

                # cosine similarity as logits
                
                logits_per_image = logit_scale * image_features @ text_features.t()
                probs = logits_per_image.softmax(dim=-1).cpu().numpy()

                print(i, " img Label probs:", probs)
                result.append({
                    "score": probs[0][0],
                    "index": i
                })
                if (probs[0][0] > maxImage["score"]):
                    maxImage["score"] = probs[0][0]
                    maxImage["index"] = i
            t2 = time.time()
            print(t2 - t1, 's')
            return maxImage, result

    def searchInVideo(self, text: str, video_path: str):
        video_frames = getVideoFrames(video_path)
        images = self.getPreprocessImages(video_frames=video_frames)
        maxImage, result = self.newSearchInImages(text, images)
        return maxImage, result

    def searchAndcutVideo(self, text: str, video_path: str, output_name: str, images = None,):
        if images is None:
            video_frames = getVideoFrames(video_path)
            images = self.getPreprocessImages(video_frames=video_frames)
        maxImage, result = self.newSearchInImages(text, images)
        # print(maxImage)

        maxIndex = maxImage["index"]

        print(maxIndex)

        leftIndex,rightIndex = self.getRange(maxIndex, result)

        print(leftIndex, rightIndex)

        t_str = getTime(leftIndex)

        cutVideo(t_str, rightIndex - leftIndex, video_path, output_name)


searchModel = SearchModel()


img_names = []

for i in range(120):
    print("sports/image-{:0>3d}".format(i+1))
    img_names.append("toy_data/sports/image1-{:0>3d}.jpg".format(i+1))

images = searchModel.getPreprocessImages(img_names)


video_name = "toy_data/sports/sports.mp4"

querys = ['a diagram', 'a sports bracelet', 'a man on the grassland', 'two people']

part_names = []

for i, query in enumerate(querys):
    name = f'{i}.mp4'
    part_names.append(name)
    searchModel.searchAndcutVideo(query, video_name, name, images)

part_ts_names = []
for name in part_names:
    waitForFileExist(o(name))
    ts_name = o(convertToTs(o(name)))
    part_ts_names.append(ts_name)


# part_names = [o(name) for name in part_names]
# with open('file.txt', 'w') as f:
#     f.write('\n'.join([f'file {name}' for name in part_names]))
#     f.close()
[waitForFileExist(name) for name in part_ts_names]
mergeVideo(part_ts_names, "sports.mp4")


