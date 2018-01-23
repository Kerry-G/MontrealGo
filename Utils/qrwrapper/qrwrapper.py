import json

class QR_Controller():

    botController = None

    def __init__(self, botController):
        self.botController = botController

    ## IMPORTANT NOTES
    #
    # Maximum 11 quick replies
    # Passed list need to have 2 things : buttontitle, payload
    def send_quick_replies(self, intro_text, array):
        i = 0
        quick_replies = []
        for reply in array[:]:
            i = i + 1
            if i < 11:
                if ("content_type" in reply):
                 if reply["content_type"] == "location":
                    quick_replies.append({
                        "content_type": "location"
                    })
                else:
                    quick_replies.append({
                        "content_type": "text",
                        "title": reply["buttontitle"],
                        "payload": reply["payload"]
                    })

        payload = {
            "recipient": json.dumps(
                {
                    'id': self.botController.recipient_id
                    # 'id': "526372527741691" # My own recipient ID
                }
            ),
            "message": json.dumps({
                "text": intro_text,
                "quick_replies": quick_replies
                # "quick_replies":[
                #     {
                #         "content_type":"text",
                #         "title":"Search",
                #         "payload":"<POSTBACK_PAYLOAD>",
                #         "image_url":"http://example.com/img/red.png"
                #     },
                #     {
                #         "content_type":"location"
                #     },
                #     {
                #         "content_type":"text",
                #         "title":"Something Else",
                #         "payload":"<POSTBACK_PAYLOAD>"
                #     }
                # ]
            })
        }
        self.bot.send_raw(payload)
        return "success"

    def get_payload_depts(self, payload):
        # Parse payload
        payload = str(payload)
        depts = payload.split("|")
        return depts

    def get_event_type(self, payload):
        depts = self.get_payload_depts(payload)
        return depts[0]