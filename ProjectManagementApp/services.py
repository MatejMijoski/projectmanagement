from datetime import datetime, timedelta
from django.core.mail import send_mail
from AuthenticationApp.models import Account
from ProjectManagementApp.models import ProjectInvite
from projectmanagement import settings
from projectmanagement.exceptions import CustomException


def send_email(subject, message, from_email, to_email_list):
    success = send_mail(subject, message, from_email, [to_email_list])
    return success


# TODO Add links for the projects
def send_invite_project(emails, project, sender):
    """
    Send invites to users that have been added to a project
    :param emails: list of emails that need to be addedd
    :param project: the project to add the users to
    :param sender: the sender of the emails i.e Account object
    :return: list of objects as JSON with messages
    """
    response = []
    for email in emails:
        # Check if user has already been invited
        try:
            invite = ProjectInvite.objects.get(project=project, email=email, sender=sender)
            # If the invite is expired and the user didn't accept/decline, send a new one and reset the expire_at field
            if invite.expire_at < datetime.today():
                try:
                    Account.objects.get(email=email)
                    send_email("You have been added to a project", "Click on the link to accept the invite.",
                               sender.email,
                               [email, ])
                    response.append({"message": "An invite has been sent to the user with an email {}.".format(email)})
                except Account.DoesNotExist:
                    # If user doesn't have an account, send an email and add the project once he creates an account
                    # There's no need to add a link to this email
                    send_email("You have been added to a project.",
                               "Please create an account to be able to access the project.", sender.email, [email, ])
                    response.append({"message": "An invite has been sent to the user with an email {}.".format(email)})
                invite.expire_at = datetime.now() + timedelta(days=10)
                invite.save()
                response.append({"message": "A new invite has been sent to the user with an email {}.".format(email)})
            else:
                response.append({"message": "The user with an email {} has already been added.".format(email)})
        except ProjectInvite.DoesNotExist:
            project_invite = ProjectInvite.objects.create(project=project, email=email, sender=sender)
            try:
                Account.objects.get(email=email)
                send_email("You have been added to a project",
                           "Click on the link to accept the invite - {}.".format(settings.SITE_URL + '/invite/' + str(project_invite.id)),
                           sender.email,
                           [email, ])
                response.append({"message": "An invite has been sent to the user with an email {}.".format(email)})
            except Account.DoesNotExist:
                # If user doesn't have an account, send an email and add the project once he creates an account
                # There's no need to add a link to this email
                send_email("You have been added to a project.",
                           "Please create an account to be able to access the project.", sender.email, [email, ])
                response.append({"message": "An invite has been sent to the user with an email {}.".format(email)})
                response.append({"message": "The user with an email {} has been succesfully invited.".format(email)})
    return response


def accept_project_invite(user, invite_id=None):
    """
    Add the users with invites to the projects
    :param user: The user that accepted the invite - Account Object
    :param invite_id: The ID of the invite. If it's None, this function was called from the Sign Up View
    :return: list of objects with a response for each invite
    """
    # If invite_id is not None, add the user
    if invite_id:
        try:
            invite = ProjectInvite.objects.get(id=invite_id, email=user.email)
            invite.add_user(user)
            return {"message": "You have succesfully been added to the project {}.".format(invite.project.name)}
        except ProjectInvite.DoesNotExist:
            raise CustomException(404, "No invite was found.")
    # If the invite_id is None, this function has been called for Sign Up
    else:
        # Find all of the invites and add the user
        invites = ProjectInvite.objects.filter(email=user.email)
        response = []
        for invite in invites:
            if invite.add_user(user):
                response.append({"message": "You have been added to project {}".format(invite.project.name)})
            else:
                response.append({"message": "There was a problem with adding you to the project {}. "
                                            "Please contact the project owner and try again.".format(invite.project.name)})
        return response
