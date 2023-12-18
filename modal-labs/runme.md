# How to do training

Based on this tutorial:
https://github.com/modal-labs/llm-finetuning/tree/main

## Run the script
modal run train.py

Get the folder where the LORA is created

Then do:

 modal run inference.py --run-folder /runs/axo-2023-12-18-11-21-25-a6c8
 

## Publishing
We have to find a way to publish on HF, as Lora.

Cheers!