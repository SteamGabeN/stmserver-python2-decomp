# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\Steam\crypto.py
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Cipher import AES
main_key_sign = RSA.construct((16972286244849771984622451367228102174501719320240653652662330551811042672286869215561928929175827402752178598753445713908601088303475414633015321035251571211566978795872136026380777563265395267739035345972002870926699475330208864762370786289338571780113370443705220053580642621034990905081765661421515793197322286229310533378663925641599451069026309189868652973825372527822995378307658254979118985781849587869182040447299629997994344818433422788110169038839718660945475305838947440389938769132300261658746306829589651102747347903636404092182462550116241824059779050479962155170547507469291673134785087525867735462771,
                               998369779108810116742497139248711892617748195308273744274254738341826039546286424444819348775048670750128152867849747876976534606086789096059724766779504188915704635051302119198869268427376192219943255645411933583923498548835815574257105075843445398830198261394424709034155448296175935593045038907147987835121276143092265929765857522003315234046704493380086236406227181752690639773759910381564885451567942201551660793531581412046961847318500202889539128927129171613072773956837051742450320264942416013004138711897082646106738944678776002164289048233329862454552712571702039963458146099156364834927612038865038435329,
                               17))
network_key = RSA.construct((134539629474386922037791973580118887976202262513059806716070824872604019001549619717043869049820865778686338042804246699105615306763509624582695524159630542063424520740697096695065917367798513676047684857537002873465544160954589243833288573668688641279313120835560801603892833928651320394652562952389632548953,
                             17, 55398670960041673780267283238872483284318578681848155706617398476954596059461608118782769608749768261812021547037042758455253361608503963063462862889259625398654146184924437001549904434764958250148333879602146773194545846894891569844887509155520581612255537741780582148990843840620079165238381404172781505181))
network_key_sign = RSA.construct((134539629474386922037791973580118887976202262513059806716070824872604019001549619717043869049820865778686338042804246699105615306763509624582695524159630542063424520740697096695065917367798513676047684857537002873465544160954589243833288573668688641279313120835560801603892833928651320394652562952389632548953,
                                  55398670960041673780267283238872483284318578681848155706617398476954596059461608118782769608749768261812021547037042758455253361608503963063462862889259625398654146184924437001549904434764958250148333879602146773194545846894891569844887509155520581612255537741780582148990843840620079165238381404172781505181,
                                  17))

def get_aes_key(encryptedstring, rsakey):
    decryptedstring = rsakey.decrypt(encryptedstring)
    if len(decryptedstring) != 127:
        raise NameError, 'RSAdecrypted string not the correct length!' + str(len(decryptedstring))
    firstpasschecksum = SHA.new(decryptedstring[20:127] + '\x00\x00\x00\x00').digest()
    secondpasskey = binaryxor(firstpasschecksum, decryptedstring[0:20])
    secondpasschecksum0 = SHA.new(secondpasskey + '\x00\x00\x00\x00').digest()
    secondpasschecksum1 = SHA.new(secondpasskey + '\x00\x00\x00\x01').digest()
    secondpasschecksum2 = SHA.new(secondpasskey + '\x00\x00\x00\x02').digest()
    secondpasschecksum3 = SHA.new(secondpasskey + '\x00\x00\x00\x03').digest()
    secondpasschecksum4 = SHA.new(secondpasskey + '\x00\x00\x00\x04').digest()
    secondpasschecksum5 = SHA.new(secondpasskey + '\x00\x00\x00\x05').digest()
    secondpasstotalchecksum = secondpasschecksum0 + secondpasschecksum1 + secondpasschecksum2 + secondpasschecksum3 + secondpasschecksum4 + secondpasschecksum5
    finishedkey = binaryxor(secondpasstotalchecksum[0:107], decryptedstring[20:127])
    controlchecksum = SHA.new('').digest()
    if finishedkey[0:20] != controlchecksum:
        raise NameError, "Control checksum didn't match!"
    return finishedkey[-16:]


def verify_message(key, message):
    key = key + '\x00' * 48
    xor_a = '6' * 64
    xor_b = '\\' * 64
    key_a = binaryxor(key, xor_a)
    key_b = binaryxor(key, xor_b)
    phrase_a = key_a + message[:-20]
    checksum_a = SHA.new(phrase_a).digest()
    phrase_b = key_b + checksum_a
    checksum_b = SHA.new(phrase_b).digest()
    if checksum_b == message[-20:]:
        return True
    else:
        return False


def sign_message(key, message):
    key = key + '\x00' * 48
    xor_a = '6' * 64
    xor_b = '\\' * 64
    key_a = binaryxor(key, xor_a)
    key_b = binaryxor(key, xor_b)
    phrase_a = key_a + message
    checksum_a = SHA.new(phrase_a).digest()
    phrase_b = key_b + checksum_a
    checksum_b = SHA.new(phrase_b).digest()
    return checksum_b


def rsa_sign_message(rsakey, message):
    digest = SHA.new(message).digest()
    fulldigest = '\x00\x01' + '\xff' * 90 + '\x000!0\t\x06\x05+\x0e\x03\x02\x1a\x05\x00\x04\x14' + digest
    signature = rsakey.encrypt(fulldigest, 0)[0]
    signature = signature.rjust(128, '\x00')
    return signature


def rsa_sign_message_1024(rsakey, message):
    digest = SHA.new(message).digest()
    fulldigest = '\x00\x01' + '\xff' * 218 + '\x000!0\t\x06\x05+\x0e\x03\x02\x1a\x05\x00\x04\x14' + digest
    signature = rsakey.encrypt(fulldigest, 0)[0]
    signature = signature.rjust(256, '\x00')
    return signature


def aes_decrypt(key, IV, message):
    decrypted = ''
    cryptobj = AES.new(key, AES.MODE_CBC, IV)
    i = 0
    while i < len(message):
        cipher = message[i:i + 16]
        decrypted = decrypted + cryptobj.decrypt(cipher)
        i = i + 16

    return decrypted


def aes_encrypt(key, IV, message):
    overflow = len(message) % 16
    if overflow > 0:
        message = message + (16 - overflow) * '\x05'
    encrypted = ''
    cryptobj = AES.new(key, AES.MODE_CBC, IV)
    i = 0
    while i < len(message):
        cipher = message[i:i + 16]
        encrypted = encrypted + cryptobj.encrypt(cipher)
        i = i + 16

    return encrypted


def binaryxor(stringA, stringB):
    if len(stringA) != len(stringB):
        print "binaryxor: string lengths doesn't match!!"
        sys.exit()
    outString = ''
    for i in range(len(stringA)):
        valA = ord(stringA[i])
        valB = ord(stringB[i])
        valC = valA ^ valB
        outString = outString + chr(valC)

    return outString