#!/usr/bin/env python

import boto3, botocore, yaml, time

def loadConfig(file):
    with open(file, 'r') as stream:
        return yaml.load(stream)

def upsertIntent(   lex,
                    name,
                    description,
                    slots = [],
                    sampleUtterances = [],
                    checksum = None,
                    confirmationPrompt = None,
                    rejectionStatement = None,
                    followUpPrompt = None,
                    conclusionStatement = None,
                    dialogCodeHook = None,
                    fulfillmentActivity = dict(type = 'ReturnIntent'),
                    parentIntentSignature = None):
    """ Upsert an intent
    """
    args = dict(
        name = name,
        description = description,
        slots = slots,
        sampleUtterances = sampleUtterances,
    )

    if checksum:
        args.update(checksum = checksum)

    if confirmationPrompt:
        args.update(confirmationPrompt = confirmationPrompt)

    if rejectionStatement:
        args.update(rejectionStatement = rejectionStatement)

    if followUpPrompt:
        args.update(followUpPrompt = followUpPrompt)

    if conclusionStatement:
        args.update(conclusionStatement = conclusionStatement)

    if dialogCodeHook:
        args.update(dialogCodeHook = dialogCodeHook)

    if fulfillmentActivity:
        args.update(fulfillmentActivity = fulfillmentActivity)

    if parentIntentSignature:
        args.update(parentIntentSignature = parentIntentSignature)

    print args

    return lex.put_intent(**args)

def buildBot(lex, name, versionOrAlias = '$LATEST'):
    """ Run the build command on a bot
    """
    print "building bot"


def upsertBot(  lex,
                name,
                description,
                intents,
                clarificationPrompt,
                abortStatement,
                checksum = None,
                processBehavior = 'SAVE',
                idleSessionTTLInSeconds = 123,
                locale = 'en-US',
                childDirected = False):
    """ Upsert a bot
    """

    args = dict(
        name = name,
        description = description,
        intents = intents,
        processBehavior = processBehavior,
        locale = locale,
        childDirected = childDirected,
        clarificationPrompt = clarificationPrompt,
        abortStatement = abortStatement,
    )

    if checksum:
        args.update(checksum = checksum)

    if clarificationPrompt:
        args.update(clarificationPrompt = clarificationPrompt)

    if abortStatement:
        args.update(abortStatement = abortStatement)

    return lex.put_bot(**args)

def findBot(lex, name, versionOrAlias = '$LATEST'):
    """ Find a bot by name/version or None is returned if not found
    """
    try:
        return lex.get_bot(name = name, versionOrAlias = versionOrAlias)
    except botocore.exceptions.ClientError as ce:
        if ce.response['Error']['Code'] == 'NotFoundException':
            return None
        raise ce

def findIntent(lex, name, versionOrAlias = '$LATEST'):
    """ Find a bot by name/version or None is returned if not found
    """
    try:
        return lex.get_intent(name = name, version = versionOrAlias)
    except botocore.exceptions.ClientError as ce:
        if ce.response['Error']['Code'] == 'NotFoundException':
            return None
        raise ce


# TODO: Increase retry to 5
def findBotWithRetry(lex, name, versionOrAlias = '$LATEST', maxRetry = 1):
    """ Find a bot by name/version with retry - returns None if not found after N retries
    """
    for x in range(1, maxRetry+1):
        response = findBot(lex, name, versionOrAlias)
        if response:
            return response
        time.sleep(x * 2)

    return None

# TODO: Increase retry to 5
def findIntentWithRetry(lex, name, versionOrAlias = '$LATEST', maxRetry = 1):
    """ Find a bot by name/version with retry - returns None if not found after N retries
    """
    for x in range(1, maxRetry+1):
        response = findIntent(lex, name, versionOrAlias)
        if response:
            return response
        time.sleep(x * 2)
    return None

def upsertBotAndIntents(lex, bot):
    """ Create the bot and the intent(s)
    """
    intents = []
    for intent in bot['intents']:
        lexIntent = findIntentWithRetry(lex, intent['name'])
        intentChecksum = None
        if lexIntent:
            intentChecksum = lexIntent['checksum']

        lexIntent = upsertIntent(lex, intent['name'], intent['name'], [], intent['sample-utterances'], intentChecksum)

        intents.append(dict(intentName = intent['name'], intentVersion = lexIntent['version']))

    lexBot = findBotWithRetry(lex, bot['name'], bot['version'])

    botChecksum = None
    if lexBot:
        botChecksum = lexBot['checksum']

    clarificationPrompt = dict(
       maxAttempts = bot['clarification-prompt']['max-attempts'],
    )

    clarificationMessages = []
    for message in bot['clarification-prompt']['messages']:
        clarificationMessages.append(
            dict(
                contentType = message['content-type'],
                content = message['content'],
            )
        )

    abortStatementMessages = []
    for message in bot['abort-statement']['messages']:
        abortStatementMessages.append(
            dict(
                contentType = message['content-type'],
                content = message['content'],
            )
        )

    clarificationPrompt = dict(
        messages = clarificationMessages,
        maxAttempts = bot['clarification-prompt']['max-attempts'],
    )

    abortStatement = dict(messages = abortStatementMessages)

    lexBot = upsertBot(
        lex,
        bot['name'],
        bot['description'],
        intents,
        clarificationPrompt,
        abortStatement,
        botChecksum,
    )

    print lexBot

def main():
    lex = boto3.client('lex-models')

    config = loadConfig('my_bots.yml')

    for bot in config['bots']:
        print 'BOT: ' + bot['name'] + ' - upserting'
        upsertBotAndIntents(lex, bot)

        print bot['name']


if __name__ == '__main__':
    main()