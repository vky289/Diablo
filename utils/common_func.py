from notifications.signals import notify


def send_notification(sender, message, link=None):
    if link is not None:
        notify.send(sender, recipient=sender, verb=message, cta_link=link)
    else:
        notify.send(sender, recipient=sender, verb=message)
