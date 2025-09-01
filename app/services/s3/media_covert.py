# app/services/s3/media_covert.py
from app.services.s3.client import s3_client_for_mc
from app.services.s3.client import (
    MEDIA_BUCKET_NAME, 
    KMS_ALIAS_MEDIA, 
    INGEST_BUCKET, 
    KMS_ALIAS_INGEST, 
    MEDIACONVERT_ROLE_ARN,
    OUTPUT_KMS_ARN
)


def build_media_rendition_job_settings(input_key: str, output_key: str, usermeta: dict):
    """
    メディアレンディションジョブ作成

    Args:
        input_key (str): 入力キー
        output_key (str): 出力キー
        usermeta (dict): ユーザーメタデータ

    Returns:
        dict: ジョブ設定
    """
    input_s3 = f"s3://{INGEST_BUCKET}/{input_key}"

    # 出力ディレクトリ（末尾に / が必要）
    out_dir = f"s3://{MEDIA_BUCKET_NAME}/{output_key.rsplit('/', 1)[0]}/"

    # 「ファイル名そのもの」を指定することはできないので、
    # 入力名の末尾に付ける NameModifier で擬似的に制御
    # ここでは常に "_preview" を付与（例：sample_preview.mp4）
    name_modifier = "_preview"

    
    return {
        "Role": MEDIACONVERT_ROLE_ARN,
        "Settings": {
            "TimecodeConfig": {"Source": "ZEROBASED"},
            "Inputs": [{
                "FileInput": input_s3,
                "AudioSelectors": {"Audio Selector 1": {"DefaultSelection": "DEFAULT"}},
                "VideoSelector": {"ColorSpace": "FOLLOW"},
            }],
            "OutputGroups": [{
                "Name": "File Group",
                "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {
                        "Destination": out_dir,
                        "DestinationSettings": {
                            "S3Settings": {
                                "Encryption": {
                                    "EncryptionType": "SERVER_SIDE_ENCRYPTION_KMS",
                                    "KmsKeyArn": OUTPUT_KMS_ARN  # ← 環境から渡す or settingsで解決
                                }
                            }
                        }
                    }
                },
                "Outputs": [{
                    "ContainerSettings": {"Container": "MP4"},
                    "VideoDescription": {
                        "Height": 480, "Width": 854,
                        "CodecSettings": {"Codec": "H_264","H264Settings": {
                            "RateControlMode": "QVBR",
                            "QvbrSettings": {"QvbrQualityLevel": 7},
                            "GopSize": 90, "GopSizeUnits": "FRAMES",
                            "MaxBitrate": 1_200_000
                        }},
                    },
                    "AudioDescriptions": [{
                        "CodecSettings": {"Codec": "AAC","AacSettings": {
                            "Bitrate": 96_000, "CodingMode": "CODING_MODE_2_0", "SampleRate": 48_000
                        }}
                    }],
                    "NameModifier": name_modifier,
                }],
            }],
        },
        "StatusUpdateInterval": "SECONDS_30",
        "Priority": 0,
        "UserMetadata": usermeta,
        "Tags": {"type": "rendition", "app": "mij"},
    }

def build_preview_mp4_settings(input_key: str, output_key: str, usermeta: dict):
    """
    プレビューMP4ジョブ作成

    Args:
        input_key (str): 入力キー
        output_key (str): 出力キー
        usermeta (dict): ユーザーメタデータ

    Returns:
        dict: ジョブ設定
    """
    input_s3  = f"s3://{INGEST_BUCKET}/{input_key}"
    out_dir   = f"s3://{MEDIA_BUCKET_NAME}/{output_key.rsplit('/',1)[0]}/"
    out_name  = output_key.split("/")[-1]
    return {
        "Role": MEDIACONVERT_ROLE_ARN,
        "Settings": {
            "TimecodeConfig": {"Source": "ZEROBASED"},
            "Inputs": [{
                "FileInput": input_s3,
                "AudioSelectors": {"Audio Selector 1": {"DefaultSelection": "DEFAULT"}},
                "VideoSelector": {"ColorSpace": "FOLLOW"},
            }],
            "OutputGroups": [{
                "Name": "File Group",
                "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {
                        "Destination": out_dir,
                        "DestinationSettings": {
                            "S3Settings": {
                                "Encryption": {
                                    "EncryptionType": "SERVER_SIDE_ENCRYPTION_KMS",
                                    "KmsKeyArn": OUTPUT_KMS_ARN
                                }
                            }
                        }
                    }
                },
                "Outputs": [{
                    "ContainerSettings": {"Container": "MP4"},
                    "VideoDescription": {
                        "Height": 480, "Width": 854,
                        "CodecSettings": {"Codec": "H_264","H264Settings": {
                            "RateControlMode": "QVBR",
                            "QvbrSettings": {"QvbrQualityLevel": 7},
                            "GopSize": 90, "GopSizeUnits": "FRAMES",
                            "MaxBitrate": 1_200_000
                        }},
                    },
                    "AudioDescriptions": [{
                        "CodecSettings": {"Codec": "AAC","AacSettings": {
                            "Bitrate": 96_000, "CodingMode": "CODING_MODE_2_0", "SampleRate": 48_000
                        }}
                    }],
                    "OutputName": out_name,
                }],
            }],
        },
        "StatusUpdateInterval": "SECONDS_30",
        "Priority": 0,
        "UserMetadata": usermeta,
        "Tags": {"type": "preview", "app": "mij"},
    }

def build_hls_abr4_settings(input_key: str, output_prefix: str, usermeta: dict):
    """
    HLS ABR4ジョブ作成

    Args:
        input_key (str): 入力キー
        output_prefix (str): 出力プレフィックス
        usermeta (dict): ユーザーメタデータ

    Returns:
        dict: ジョブ設定
    """
    input_s3 = f"s3://{INGEST_BUCKET}/{input_key}"
    dest     = f"s3://{MEDIA_BUCKET_NAME}/{output_prefix.strip('/')}/"  # ★ 末尾 / を必ず付与

    def stream(h, w, max_br, a_br, name, profile="HIGH"):
        return {
            "VideoDescription": {
                "Height": h, "Width": w,
                "CodecSettings": {
                    "Codec": "H_264",
                    "H264Settings": {
                        "RateControlMode": "QVBR",
                        "MaxBitrate": max_br,
                        "QvbrSettings": {"QvbrQualityLevel": 7},
                        "GopSizeUnits": "SECONDS",
                        "GopSize": 2.0,
                        "NumberBFramesBetweenReferenceFrames": 2,
                        "AdaptiveQuantization": "HIGH",
                        "SceneChangeDetect": "TRANSITION_DETECTION",
                        "SlowPal": "DISABLED",
                        "FramerateControl": "INITIALIZE_FROM_SOURCE",
                        "ParControl": "INITIALIZE_FROM_SOURCE",
                        "Syntax": "DEFAULT",
                        "Level": "LEVEL_AUTO",
                        "Profile": profile
                    }
                }
            },
            "AudioDescriptions": [{
                "CodecSettings": {
                    "Codec": "AAC",
                    "AacSettings": {
                        "Bitrate": a_br,
                        "CodingMode": "CODING_MODE_2_0",
                        "SampleRate": 48000
                    }
                },
                # 音量のばらつき抑制（お好みで）
                "AudioNormalizationSettings": {
                    "Algorithm": "ITU_BS_1770_4",
                    "AlgorithmControl": "CORRECT_AUDIO"
                }
            }],
            "ContainerSettings": {"Container": "M3U8"},
            "NameModifier": name
        }

    return {
        "Role": MEDIACONVERT_ROLE_ARN,
        "Settings": {
            "TimecodeConfig": {"Source": "ZEROBASED"},
            "Inputs": [{
                "FileInput": input_s3,
                "AudioSelectors": {"Audio Selector 1": {"DefaultSelection": "DEFAULT"}},
                "VideoSelector": {"ColorSpace": "FOLLOW"},
            }],
            "OutputGroups": [{
                "Name": "HLS",
                "OutputGroupSettings": {
                    "Type": "HLS_GROUP_SETTINGS",
                    "HlsGroupSettings": {
                        "Destination": dest,
                        "SegmentLength": 6,
                        "MinSegmentLength": 0,
                        "MinFinalSegmentLength": 0,
                        "DirectoryStructure": "SINGLE_DIRECTORY",
                        "ManifestDurationFormat": "INTEGER",
                        "OutputSelection": "MANIFESTS_AND_SEGMENTS",
                        "SegmentControl": "SEGMENTED_FILES",
                        "CodecSpecification": "RFC_6381",
                        # （任意）マニフェスト圧縮
                        # "ManifestCompression": "GZIP",
                        "DestinationSettings": {
                            "S3Settings": {
                                "Encryption": {
                                    "EncryptionType": "SERVER_SIDE_ENCRYPTION_KMS",
                                    "KmsKeyArn": OUTPUT_KMS_ARN
                                }
                            }
                        }
                    }
                },
                "Outputs": [
                    # 360p 16:9
                    stream(360,   640,   800_000,   96_000, "_360p"),
                    # 480p
                    stream(480,   854, 1_200_000,   96_000, "_480p"),
                    # 720p
                    stream(720,  1280, 2_500_000,  128_000, "_720p"),
                    # 1080p（HIGH プロファイル指定のまま）
                    stream(1080, 1920, 4_500_000,  128_000, "_1080p"),
                ]
            }]
        },
        "StatusUpdateInterval": "SECONDS_30",
        "Priority": 0,
        "UserMetadata": usermeta,
        "Tags": {"type": "final-hls", "app": "mij"},
    }