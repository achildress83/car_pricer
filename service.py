import modal
from modal import App, Image
from config_deploy import GPU

# define infrastructure with code
app = App('car-pricer')
image = Image.debian_slim().pip_install("huggingface", "torch", "transformers", "bitsandbytes", "accelerate", "peft", "python-dotenv")
secrets = [modal.Secret.from_name('hf-secret')]


@app.cls(image=image, secrets=secrets, gpu=GPU, timeout=1800)
class Pricer:
    QUESTION = "How much does this cost to the nearest dollar?"
    PREFIX = "Price is $"
    
    @modal.build()
    def download_model_to_folder(self):
        from huggingface_hub import snapshot_download
        import os
        from config_deploy import MODEL_DIR, BASE_MODEL, BASE_DIR, FINETUNED_MODEL, REVISION, FINETUNED_DIR
        os.makedirs(MODEL_DIR, exist_ok=True)
        snapshot_download(BASE_MODEL, local_dir=BASE_DIR)
        snapshot_download(FINETUNED_MODEL, revision=REVISION, local_dir=FINETUNED_DIR)
            
    @modal.enter()
    def setup(self):
        import os
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, set_seed
        from peft import PeftModel
        from config_deploy import QUANT_4_BIT, BASE_MODEL, FINETUNED_MODEL, REVISION
        # Quant Config
        if QUANT_4_BIT:
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4"
            )
        else:
            quant_config = BitsAndBytesConfig(
                load_in_8bit=True,
                bnb_8bit_compute_dtype=torch.bfloat16
            )

        # Load model and tokenizer
        
        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        self.base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL, 
            quantization_config=quant_config,
            device_map="auto"
        )

        if REVISION:
            self.fine_tuned_model = PeftModel.from_pretrained(self.base_model, FINETUNED_MODEL, revision=REVISION)
        else:
            self.fine_tuned_model = PeftModel.from_pretrained(self.base_model, FINETUNED_MODEL)

    
    @modal.method()
    def price(self, description: str) -> float:

        try:
            import re
            import torch
            from transformers import set_seed
            from config_deploy import SEED, MAX_NEW_TOKENS
            
            prompt = f"{self.QUESTION}\n{description}\n{self.PREFIX}"
            
            set_seed(SEED)
            
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to("cuda")
            attention_mask = torch.ones(inputs.shape, device="cuda")
            outputs = self.fine_tuned_model.generate(inputs, 
                                                     attention_mask=attention_mask, 
                                                     max_new_tokens=MAX_NEW_TOKENS, 
                                                     num_return_sequences=1)
            result = self.tokenizer.decode(outputs[0])

            contents = result.split("Price is $")[1]
            contents = contents.replace(',','')
            match = re.search(r"[-+]?\d*\.\d+|\d+", contents)
            return float(match.group()) if match else 0
        except Exception as e:
            print(f'Error during price prediction: {e}')
    
    @modal.method()
    def wake_up(self) -> str:
        return "ok"