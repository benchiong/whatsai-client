from data_type.whatsai_model_info import ModelInfo
from tiny_db.model_info import ModelInfoTable


def tae_model_info_list():
    taes = ModelInfoTable.sync_get_taesd_file_records()

    sdxl_taesd_enc = None
    sdxl_taesd_dec = None
    sd1_taesd_enc = None
    sd1_taesd_dec = None
    sd3_taesd_enc = None
    sd3_taesd_dec = None
    f1_taesd_enc = None
    f1_taesd_dec = None

    for vae in taes:
        v = vae.get('file_name')
        if v.startswith("taesd_decoder."):
            sd1_taesd_dec = vae
        elif v.startswith("taesd_encoder."):
            sd1_taesd_enc = vae
        elif v.startswith("taesdxl_decoder."):
            sdxl_taesd_dec = vae
        elif v.startswith("taesdxl_encoder."):
            sdxl_taesd_enc = vae
        elif v.startswith("taesd3_decoder."):
            sd3_taesd_dec = vae
        elif v.startswith("taesd3_encoder."):
            sd3_taesd_enc = vae
        elif v.startswith("taef1_encoder."):
            f1_taesd_dec = vae
        elif v.startswith("taef1_decoder."):
            f1_taesd_enc = vae

    tae_model_info_list = []

    def merge_enc_dec(enc, dec):
        model_info = ModelInfo(
            local_path='{}|{}'.format(enc.get('local_path'), dec.get('local_path')),
            file_name='{}|{}'.format(enc.get('file_name'), dec.get('file_name')),
            sha_256='{}|{}'.format(enc.get('sha_256'), dec.get('sha_256')),
            model_type=enc.get('model_type'),
        )
        return model_info.model_dump()

    if sd1_taesd_dec and sd1_taesd_enc:
        tae_model_info_list.append(merge_enc_dec(sd1_taesd_dec, sd1_taesd_enc))
    if sdxl_taesd_dec and sdxl_taesd_enc:
        tae_model_info_list.append(merge_enc_dec(sdxl_taesd_dec, sdxl_taesd_enc))
    if sd3_taesd_dec and sd3_taesd_enc:
        tae_model_info_list.append(merge_enc_dec(sd3_taesd_dec, sd3_taesd_enc))
    if f1_taesd_dec and f1_taesd_enc:
        tae_model_info_list.append(merge_enc_dec(f1_taesd_dec, f1_taesd_enc))
    return tae_model_info_list