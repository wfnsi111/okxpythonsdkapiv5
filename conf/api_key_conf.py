# flag是实盘与模拟盘的切换参数 1是模拟，， 0是实盘

# 模拟
api_key1 = {
    'api_key': "f76a1e05-cc56-43fd-aa6a-88aa3e51b6a2",
    'secret_key': "A23C7CEB8046F39369CF73BDEBE985F5",
    'passphrase': "Kangkang1_",
    'flag': '1'
}

# 200
api_key2 = {
    'api_key': "47473a01-7149-4deb-ac31-ee54a3afc124",
    'secret_key': "79AADC7A194FD4548AFEB12AC9F78D13",
    'passphrase': "Lch798503@",
    'flag': '0'
}

# 50u
api_key3 = {
    'api_key': "d4c23806-6c64-432e-96f6-b0e5a62042e8",
    'secret_key': "6424FB773D9F8C8573B2477C0D0040EE",
    'passphrase': "Lch798503@",
    'flag': '0'
}

# huangA
api_key4 = {
    'api_key': "2047c208-990d-4b11-b0ea-a3dcf38a97a6",
    'secret_key': "A16F8E1051E54AD1BDAF4E0EB4892121",
    'passphrase': "Aa123456a@",
    'flag': '0'
}

# huangB
api_key5 = {
    'api_key': "b1f4ff7c-277e-48ab-87c1-ad8cba921e12",
    'secret_key': "E69C1A38D4B61C5D706F1B52FEC063FD",
    'passphrase': "Aa123123@",
    'flag': '0'
}

# zhangA
api_key6 = {
    'api_key': "162fd29c-028b-447f-b1e4-4387358ee82b",
    'secret_key': "277B773B109BBBADEF46AF542143D41C",
    'passphrase': "Zwl070916.",
    'flag': '0'
}

# zhangB
api_key7 = {
    'api_key': "ac01c713-305f-4c62-8e8b-6ddb4115eee6",
    'secret_key': "3C98F7C833834D8C31D37913921E48FB",
    'passphrase': "Zwl070916.",
    'flag': '0'
}


def get_aip_key(name):
    if name == "huangA":
        return api_key4
    if name == "huangB":
        return api_key5
    if name == "zhangA":
        return api_key6
    if name == "zhangB":
        return api_key7
    if name == '模拟':
        return api_key1
