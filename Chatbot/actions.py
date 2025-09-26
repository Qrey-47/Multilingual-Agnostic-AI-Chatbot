# actions.py
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# Multilingual responses dictionary
responses = {
    "greet": {
        "en": "Hello! How can I help you today?",
        "hi": "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?",
        "mr": "नमस्कार! मी तुमची कशी मदत करू शकतो?"
    },
    "ask_fees": {
        "en": "The last date for fee payment is 30th September 2025.",
        "hi": "शुल्क भुगतान की अंतिम तिथि 30 सितम्बर 2025 है।",
        "mr": "शुल्क भरण्याची शेवटची तारीख ३० सप्टेंबर २०२५ आहे."
    },
    "ask_followup_fees": {
        "en": "You can pay fees online at the student portal, cash counter, DD, or cheque. Late fee charges may apply.",
        "hi": "आप छात्र पोर्टल ऑनलाइन/कैश काउंटर/डीडी/चेक से शुल्क जमा कर सकते हैं। विलंब शुल्क लागू हो सकता है।",
        "mr": "तुम्ही विद्यार्थी पोर्टल ऑनलाइन/कॅश काउंटर/डीडी/चेक शुल्क भरू शकता. विलंब शुल्क लागू होऊ शकते."
    },
    "ask_scholarship": {
        "en": "You can collect the scholarship form from the admin office or download it from the college website.",
        "hi": "आप छात्रवृत्ति फॉर्म प्रशासन कार्यालय से प्राप्त कर सकते हैं या कॉलेज की वेबसाइट से डाउनलोड कर सकते हैं।",
        "mr": "तुम्ही शिष्यवृत्ती फॉर्म प्रशासकीय कार्यालयातून घेऊ शकता किंवा महाविद्यालयाच्या वेबसाइटवरून डाउनलोड करू शकता."
    },
    "ask_followup_scholarship": {
        "en": "Required documents: Aadhar, PAN card, and previous academic year's marksheets.",
        "hi": "आवश्यक दस्तावेज: आधार, पैन कार्ड और पिछली शैक्षणिक वर्ष की मार्कशीट।",
        "mr": "आवश्यक कागदपत्रे: आधार, पॅन कार्ड आणि मागील शैक्षणिक वर्षाची मार्कशीट."
    },
    "ask_timetable": {
        "en": "Updates regarding the timetable are posted on Classroom WhatsApp official groups.",
        "hi": "समय सारिणी से संबंधित अपडेट क्लासरूम व्हाट्सएप आधिकारिक समूहों पर पोस्ट किए जाते हैं।",
        "mr": "वेळापत्रकाबाबतचे अपडेट्स अधिकृत क्लासरूम व्हॉट्सअॅप ग्रुपवर पोस्ट केले जातात."
    },
    "ask_library": {
        "en": "The library is open from 8 AM to 6 PM on working days.",
        "hi": "पुस्तकालय सुबह 8 बजे से शाम 6 बजे तक खुला रहता है।",
        "mr": "ग्रंथालय सकाळी ८ ते संध्याकाळी ६ पर्यंत उघडते."
    },
    "ask_followup_library": {
        "en": "You can borrow only 1 book at a time. Late fine ₹10 applies.",
        "hi": "आप एक बार में केवल एक ही पुस्तक उधार ले सकते हैं। देर से लौटाने पर 10 रुपये का जुर्माना लगेगा।",
        "mr": "तुम्ही एका वेळी फक्त १ पुस्तक उधार घेऊ शकता. उशिरा परत केल्यास १० रुपये दंड लागेल."
    },
    "ask_events": {
        "en": "The list of college events and sports is available on the website.",
        "hi": "कॉलेज में आयोजित कार्यक्रमों और खेलों की सूची वेबसाइट पर उपलब्ध है।",
        "mr": "महाविद्यालयातील कार्यक्रमांची यादी वेबसाइटवर उपलब्ध आहे."
    },
    "ask_contact": {
        "en": "You can contact the admin office at +91-1234567890.",
        "hi": "आप प्रशासन कार्यालय से +91-1234567890 पर संपर्क कर सकते हैं।",
        "mr": "तुम्ही प्रशासन कार्यालयाशी +91-1234567890 वर संपर्क करू शकता."
    },
    "ask_holidays": {
        "en": "Semester holidays start on 15th December 2025. College reopens on 6th January 2026.",
        "hi": "सेमेस्टर की छुट्टियां 15 दिसंबर 2025 से शुरू होंगी। कॉलेज 6 जनवरी 2026 को पुनः खुलेगा।",
        "mr": "सेमिस्टरची सुट्टी १५ डिसेंबर २०२५ पासून सुरू होईल. कॉलेज ६ जानेवारी २०२६ रोजी पुन्हा सुरू होईल."
    },
    "ask_exam": {
        "en": "IA exams start on 10th October 2025. Viva on 22nd November, semester exams from 1st December 2025.",
        "hi": "आईए परीक्षाएं 10 अक्टूबर 2025 से शुरू होंगी। मौखिक 22 नवंबर से। सेमेस्टर 1 दिसंबर से।",
        "mr": "आयए परीक्षा १० ऑक्टोबर २०२५ पासून सुरू होतील. तोंडी २२ नोव्हेंबरपासून. सेमिस्टर १ डिसेंबरपासून."
    },
    "ask_followup_exam": {
        "en": "Exam dates are tentative and may change.",
        "hi": "परीक्षा की तिथियां अस्थायी हैं और बदल सकती हैं।",
        "mr": "परीक्षेच्या तारखा अनिश्चित आहेत आणि बदल होऊ शकतात."
    },
    "ask_hostel": {
        "en": "Hostel timings are 7 AM to 10 PM. Rules are on notice board.",
        "hi": "हॉस्टल का समय सुबह 7 बजे से रात 10 बजे तक है। नियम बोर्ड पर हैं।",
        "mr": "हॉस्टल वेळ सकाळी ७ ते रात्री १० पर्यंत आहे. नियम बोर्डवर आहेत."
    },
    "ask_followup_hostel": {
        "en": "The hostel is 10 mins away from college. Check website for details.",
        "hi": "हॉस्टल कॉलेज से 10 मिनट दूर है। वेबसाइट देखें।",
        "mr": "वसतिगृह महाविद्यालयापासून १० मिनिटांच्या अंतरावर आहे. वेबसाइट पहा."
    },
    "out_of_scope": {
        "en": "I'm sorry, I can only help with college-related queries like fees, scholarship, library, exams, hostel, events, contact, holidays, and timetable information.",
        "hi": "क्षमा करें, मैं केवल कॉलेज से संबंधित जानकारी में मदद कर सकता हूँ जैसे कि शुल्क, छात्रवृत्ति, पुस्तकालय, परीक्षा, हॉस्टल, कार्यक्रम, संपर्क, छुट्टियाँ और समय सारिणी।",
        "mr": "माफ करा, मी फक्त कॉलेजशी संबंधित प्रश्नांमध्ये मदत करू शकतो जसे की शुल्क, शिष्यवृत्ती, ग्रंथालय, परीक्षा, वसतिगृह, कार्यक्रम, संपर्क, सुट्ट्या आणि वेळापत्रक."
    }
}

def detect_language(message: Text) -> Text:
    """Detect language from user message"""
    if not message:
        return "en"
    
    # Count Devanagari characters
    devanagari_count = sum(1 for c in message if '\u0900' <= c <= '\u097F')
    
    if devanagari_count == 0:
        return "en"
    
    # Simple Marathi vs Hindi detection
    marathi_words = ['आहे', 'काय', 'कुठे', 'कसे', 'कधी', 'येणारे', 'तुम्ही', 'मी', 'आम्ही']
    hindi_words = ['है', 'क्या', 'कहाँ', 'कैसे', 'कब', 'आने वाले', 'आप', 'मैं', 'हम']
    
    marathi_score = sum(1 for word in marathi_words if word in message)
    hindi_score = sum(1 for word in hindi_words if word in message)
    
    return "mr" if marathi_score > hindi_score else "hi"

class ActionDynamicResponse(Action):
    def name(self) -> Text:
        return "action_dynamic_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get intent and user message
        last_intent = tracker.latest_message['intent'].get('name')
        user_message = tracker.latest_message.get('text', '')
        
        # Detect language
        lang = detect_language(user_message)
        
        # Get appropriate response
        if last_intent in responses:
            if lang in responses[last_intent]:
                text = responses[last_intent][lang]
            else:
                # Fallback to English if language not available
                text = responses[last_intent].get("en", responses["out_of_scope"]["en"])
        else:
            # Unknown intent - use out_of_scope
            text = responses["out_of_scope"].get(lang, responses["out_of_scope"]["en"])
        
        dispatcher.utter_message(text=text)
        return []