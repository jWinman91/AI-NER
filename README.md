# AI-Name-Entity-Recognizer (AI-NER): Text Editing with Language Models


This repository is designed for editing input text using a Language Model.
It allows users to apply various editing prompts and various models defined in configuration files to modify the input text.

Currently, the editing prompts are written to recognize and replace name entities such as names or locations from free text
and replaces all occurrences with a placeholder defined in the prompt config file.

It functions in a way like a smart editor.
E.g. it can anonymize names in a text or exchange name entities for a batch of emails.

## Installation

To use the AI-NER , follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/jWinman91/ai-extractor.git
cd ai-extractor
```
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Optional: Download a model of your choice into `model`

## Configuration

In order to use this repository, several configuration need to be set.

## Usage

You can simply use AI-NER by running:

````bash
python main.py
````

## Example

An example text file is added in `data/input/email_example_de.txt`, which is a random email.
By applying AI-NER to this file, we can now anonymize all names and locations in this email.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [NLTK](https://www.nltk.org/) - Natural Language Toolkit used for sentence tokenization.
- [Hugging Face](https://huggingface.co/) - Framework for working with state-of-the-art natural language processing models.
