from notifications.signals import notify


def send_notification(sender, message):
    notify.send(sender, recipient=sender, verb=message)
