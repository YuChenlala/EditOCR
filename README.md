# EditOCR : An Interactive Platform for Promoting Industrial Document Digitization

This is the code of our platform **EditOCR**, which is a novel editable interactive platform for processing industrial documents.

## Directory Structure

The project consists of the following directories:

- **backend/**: Directory containing backend code
- **frontend/**: Directory containing frontend code
- **LICENSE**: Project license file
- **README.md**: Main README file of the project, containing project overview, usage instructions, etc.

## Requirements

To successfully run and develop this project, you will need the following:

- **Frontend**:
  - Built using the React framework. For environment setup, refer to the official React documentation [here](https://reactjs.org/docs/getting-started.html).

- **Backend**:
  - Developed using the Flask framework. For environment setup, refer to the official Flask documentation [here](https://flask.palletsprojects.com/en/2.1.x/).

## Using the model
To run the model you need Python 3.7+

If you don't have PyTorch installed. Follow their instructions [here](https://pytorch.org/get-started/locally/).

```python
from model.OCR import image_to_text
image_path = 'path/to/image.png'
data_text = image_to_text(image_path)
print(datatext)
```

## Online Demo
See: https://yuchenlala.github.io/my-web/

## License

This project is licensed under the [MIT License](LICENSE).
