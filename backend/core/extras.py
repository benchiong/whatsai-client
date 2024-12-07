from data_type.whatsai_model_info import ModelInfo


def tae_model_info_list():
    taes = ModelInfo.get_taesd_model_infos()

    sdxl_taesd_enc = None
    sdxl_taesd_dec = None
    sd1_taesd_enc = None
    sd1_taesd_dec = None
    sd3_taesd_enc = None
    sd3_taesd_dec = None
    f1_taesd_enc = None
    f1_taesd_dec = None

    for tae in taes:
        tae_filename = tae.file_name
        if tae_filename.startswith("taesd_decoder."):
            sd1_taesd_dec = tae
        elif tae_filename.startswith("taesd_encoder."):
            sd1_taesd_enc = tae
        elif tae_filename.startswith("taesdxl_decoder."):
            sdxl_taesd_dec = tae
        elif tae_filename.startswith("taesdxl_encoder."):
            sdxl_taesd_enc = tae
        elif tae_filename.startswith("taesd3_decoder."):
            sd3_taesd_dec = tae
        elif tae_filename.startswith("taesd3_encoder."):
            sd3_taesd_enc = tae
        elif tae_filename.startswith("taef1_encoder."):
            f1_taesd_dec = tae
        elif tae_filename.startswith("taef1_decoder."):
            f1_taesd_enc = tae

    tae_model_info_list = []

    def merge_enc_dec(enc, dec):
        model_info = ModelInfo(
            local_path='{}|{}'.format(enc.local_path, dec.local_path),
            file_name='{}|{}'.format(enc.file_name, dec.file_name),
            sha_256='{}|{}'.format(enc.sha_256, dec.sha_256),
            model_type=enc.model_type,
        )
        return model_info

    if sd1_taesd_dec and sd1_taesd_enc:
        tae_model_info_list.append(merge_enc_dec(sd1_taesd_dec, sd1_taesd_enc))
    if sdxl_taesd_dec and sdxl_taesd_enc:
        tae_model_info_list.append(merge_enc_dec(sdxl_taesd_dec, sdxl_taesd_enc))
    if sd3_taesd_dec and sd3_taesd_enc:
        tae_model_info_list.append(merge_enc_dec(sd3_taesd_dec, sd3_taesd_enc))
    if f1_taesd_dec and f1_taesd_enc:
        tae_model_info_list.append(merge_enc_dec(f1_taesd_dec, f1_taesd_enc))
    return tae_model_info_list