from googletrans import Translator


def translate_text_googletrans(text, dest_language='ml'):
    translator = Translator()
    translation = translator.translate(text, dest=dest_language)
    return translation.text


if __name__ == "__main__":
    text_to_translate = """Dear Friends, 
    
    We kindly request your urgent cooperation in returning the cash and coupon books for the Faith Hall construction 
    fund. 
    
    Only six families contributed so far. The Parish is in urgent need of fund.

    Please hand over the cash and books on coming Sundays. 

    Your cooperation in this regard is greatly appreciated"""

    translated_text = translate_text_googletrans(text_to_translate)
    print(f"Translated Text: {translated_text}")
