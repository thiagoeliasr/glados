#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import requests
import os

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Consultar CNPJ', 'Consultar CEP'],
                  ['Manda Bullshit', 'Sobre'],
                  ['Pronto']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

def start(update, context):
    update.message.reply_text(
        "Olá. Eu sou a GlaDOS. Sua IA preferida. Me informe o que deseja "
        "e vou tentar procurar para você",
        reply_markup=markup)

    return CHOOSING


def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text

    if text.lower() == 'consultar cnpj':
        update.message.reply_text(
            'Ok, me informe o CNPJ sem pontuação:'
        )

    if text.lower() == 'consultar cep':
        update.message.reply_text(
            'Beleza, me manda o CEP sem pontuação:'
        )

    if text.lower() == 'manda bullshit':
        update.message.reply_text(
            'Pra já. Só copiar e colar no suporte: 😂'
        )
        get_bullshit(update)
        return CHOOSING


    return TYPING_REPLY


def about(update, context):
    update.message.reply_text(
        'Sou apenas um bot criado por http://thiagoelias.org '
        'para suprir necessidades específicas.'
    )
    return CHOOSING

def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    if category.lower() == 'consultar cnpj':
        consulta_cnpj(text, update)

    if category.lower() == 'consultar cep':
        consulta_cep(text, update)

    return CHOOSING


def done(update, context):
    update.message.reply_text('Até a próxima. 👋')
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def consulta_cnpj(cnpj, update):
    url = 'https://www.receitaws.com.br/v1/cnpj/{}'.format(cnpj)
    req = requests.get(url)
    if req.status_code != 200:
        update.message.reply_text(
            'Deu erro {} ao consultar o CNPJ. Tente de novo'.format(req.status_code)
        )

    try:
        data = req.json()

        atividades_principais = ''
        for atividade in data['atividade_principal']:
            atividades_principais += "- {} ({})\n".format(atividade['text'], atividade['code'])


        atividades_secundarias = ''
        for atividade in data['atividades_secundarias']:
            atividades_secundarias += "- {} ({})\n".format(atividade['text'], atividade['code'])

        return_text = """
Nome: {}
Fantasia: {}
Atividade Principal: 
{}
Atividades secundárias: 
{}
Tipo: {}
Data Situação: {}
Situação: {}
Abertura: {}
Logradouro: {}, Número: {}
Cidade: {} - {}
Bairro: {}
CEP: {}
CNPJ: {}
        """.format(
            data['nome'],
            data['fantasia'],
            atividades_principais,
            atividades_secundarias,
            data['tipo'],
            data['data_situacao'],
            data['situacao'],
            data['abertura'],
            data['logradouro'],
            data['numero'],
            data['municipio'],
            data['uf'],
            data['bairro'],
            data['cep'],
            data['cnpj'],
        )

        update.message.reply_text(return_text)
    except:
        update.message.reply_text('Deu erro ao consultar o CNPJ. Tente de novo')


def consulta_cep(cep, update):
    url = 'https://viacep.com.br/ws/{}/json/unicode/'.format(cep)
    req = requests.get(url)
    if req.status_code != 200:
        update.message.reply_text(
            'Deu o erro {} ao consultar. Tente novamente.'.format(req.status_code)
        )

    try:
        data = req.json()
        text = """
CEP: {}
Logradouro: {}
Complemento: {}
Bairro: {}
Localidade: {}
UF: {}
Unidade: {}
IBGE: {}
GIA: {}
    """. format(
            data['cep'],
            data['logradouro'],
            data['complemento'],
            data['bairro'],
            data['localidade'],
            data['uf'],
            data['unidade'],
            data['ibge'],
            data['gia']
        )

        update.message.reply_text(text)
    except:
        'Deu um erro ao pesquisar o CEP. Tenta de novo'

def get_bullshit(update):
    url = 'http://bs.thiagoelias.org/api/phrase'
    req = requests.get(url)
    if req.status_code != 200:
        update.message.reply_text(
            'Deu o erro {}. Tenta de novo daqui a pouco'.format(req.status_code)
        )
    
    try:
        retorno = req.json()
        update.message.reply_text(retorno['message'])
    except:
        update.message.reply_text(
            'Vixe. Deu um erro aqui. Tenta de novo'
        )

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.environ['BOT_TOKEN'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [
                MessageHandler(Filters.regex(
                '^((?i)Consultar CNPJ|(?i)Consultar CEP|(?i)Manda Bullshit)$'
                ), regular_choice),
                MessageHandler(Filters.regex('^(?i)Sobre$'), about)
            ],
            TYPING_CHOICE: [MessageHandler(Filters.text, regular_choice)],
            TYPING_REPLY: [MessageHandler(Filters.text, received_information)],
        },

        fallbacks=[MessageHandler(Filters.regex('^(?i)Pronto$'), done)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()