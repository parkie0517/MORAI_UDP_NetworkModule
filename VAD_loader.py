# ---------------------------------------------
# Copyright (c) OpenMMLab. All rights reserved.
# ---------------------------------------------
#  Modified by Zhiqi Li
# ---------------------------------------------
import sys
sys.path.append('/mnt/ssd_e2e/VAD')
sys.path.append('/mnt/ssd_e2e')
import numpy as np
import argparse
import mmcv
import os
import copy
import torch
torch.multiprocessing.set_sharing_strategy('file_system')
import warnings
from mmcv import Config, DictAction
from mmcv.cnn import fuse_conv_bn
from mmcv.parallel import MMDataParallel, MMDistributedDataParallel
from mmcv.runner import (get_dist_info, init_dist, load_checkpoint,
                         wrap_fp16_model)

from mmdet3d.apis import single_gpu_test
from mmdet3d.datasets import build_dataset
from projects.mmdet3d_plugin.datasets.builder import build_dataloader
from mmdet3d.models import build_model
from mmdet.apis import set_random_seed
# from projects.mmdet3d_plugin.bevformer.apis.test import custom_multi_gpu_test
from projects.mmdet3d_plugin.VAD.apis.test import custom_multi_gpu_test
from mmdet.datasets import replace_ImageToTensor
import time
import os.path as osp
import json
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings("ignore")

sys.path.append("/mnt/ssd_e2e/VAD/tools/data_converter")
from moraidataset import MoraiDataset

from functools import partial
from torch.utils.data import DataLoader
from mmcv.parallel import collate
import random
import os
#  CUDA_VISIBLE_DEVICES=0 python tools/test_morai.py projects/configs/VAD/VAD_base_e2e_morai.py /mnt/ssd_e2e/VAD/morai_250221_fut3sec_his2sec_fulldataset/epoch_60.pth --launcher none --eval bbox --tmpdir tmp
# CUDA_VISIBLE_DEVICES=0 python realtime_e2e_giwon_v250310.py /mnt/ssd_e2e/VAD/projects/configs/VAD/VAD_base_e2e_morai.py /mnt/ssd_e2e/VAD/morai_250221_fut3sec_his2sec_fulldataset/epoch_60.pth


def worker_init_fn(worker_id, num_workers, rank, seed):
    # The seed of each worker equals to
    # num_worker * rank + worker_id + user_seed
    worker_seed = num_workers * rank + worker_id + seed
    np.random.seed(worker_seed)
    random.seed(worker_seed)

def parse_args():
    # f'--config /mnt/ssd_e2e/VAD/projects/configs/VAD/VAD_base_e2e_morai.py --checkpoint /mnt/ssd_e2e/VAD/morai_250221_fut3sec_his2sec_fulldataset/epoch_60.pth'.split(' ')
    parser = argparse.ArgumentParser(
        description='MMDet test (and eval) a model')
    parser.add_argument('config', default="/mnt/ssd_e2e/VAD/projects/configs/VAD/VAD_base_e2e_morai.py", help='test config file path')
    parser.add_argument('checkpoint', default="/mnt/ssd_e2e/VAD/morai_250221_fut3sec_his2sec_fulldataset/epoch_60.pth", help='checkpoint file')
    parser.add_argument('--json_dir', help='json parent dir name file') # NOTE: json file parent folder name
    parser.add_argument('--out', help='output result file in pickle format')
    parser.add_argument(
        '--fuse-conv-bn',
        action='store_true',
        help='Whether to fuse conv and bn, this will slightly increase'
        'the inference speed')
    parser.add_argument(
        '--format-only',
        action='store_true',
        help='Format the output results without perform evaluation. It is'
        'useful when you want to format the result to a specific format and '
        'submit it to the test server')
    parser.add_argument(
        '--eval',
        type=str,
        nargs='+',
        help='evaluation metrics, which depends on the dataset, e.g., "bbox",'
        ' "segm", "proposal" for COCO, and "mAP", "recall" for PASCAL VOC')
    parser.add_argument('--show', action='store_true', help='show results')
    parser.add_argument(
        '--show-dir', help='directory where results will be saved')
    parser.add_argument(
        '--gpu-collect',
        action='store_true',
        help='whether to use gpu to collect results.')
    parser.add_argument(
        '--tmpdir',
        help='tmp directory used for collecting results from multiple '
        'workers, available when gpu-collect is not specified')
    parser.add_argument('--seed', type=int, default=0, help='random seed')
    parser.add_argument(
        '--deterministic',
        action='store_true',
        help='whether to set deterministic options for CUDNN backend.')
    parser.add_argument(
        '--cfg-options',
        nargs='+',
        action=DictAction,
        help='override some settings in the used config, the key-value pair '
        'in xxx=yyy format will be merged into config file. If the value to '
        'be overwritten is a list, it should be like key="[a,b]" or key=a,b '
        'It also allows nested list/tuple values, e.g. key="[(a,b),(c,d)]" '
        'Note that the quotation marks are necessary and that no white space '
        'is allowed.')
    parser.add_argument(
        '--options',
        nargs='+',
        action=DictAction,
        help='custom options for evaluation, the key-value pair in xxx=yyy '
        'format will be kwargs for dataset.evaluate() function (deprecate), '
        'change to --eval-options instead.')
    parser.add_argument(
        '--eval-options',
        nargs='+',
        action=DictAction,
        help='custom options for evaluation, the key-value pair in xxx=yyy '
        'format will be kwargs for dataset.evaluate() function')
    parser.add_argument(
        '--launcher',
        choices=['none', 'pytorch', 'slurm', 'mpi'],
        default='none',
        help='job launcher')
    parser.add_argument('--local_rank', type=int, default=0)
    args = parser.parse_args()
    if 'LOCAL_RANK' not in os.environ:
        os.environ['LOCAL_RANK'] = str(args.local_rank)

    if args.options and args.eval_options:
        raise ValueError(
            '--options and --eval-options cannot be both specified, '
            '--options is deprecated in favor of --eval-options')
    if args.options:
        warnings.warn('--options is deprecated in favor of --eval-options')
        args.eval_options = args.options
    return args


def VAD_loader():
    args = parse_args()

    '''
    assert args.out or args.eval or args.format_only or args.show \
        or args.show_dir, \
        ('Please specify at least one operation (save/eval/format/show the '
         'results / save the results) with the argument "--out", "--eval"'
         ', "--format-only", "--show" or "--show-dir"')
    
    if args.eval and args.format_only:
        raise ValueError('--eval and --format_only cannot be both specified')

    if args.out is not None and not args.out.endswith(('.pkl', '.pickle')):
        raise ValueError('The output file must be a pkl file.')
    '''
    cfg = Config.fromfile(args.config)
    if args.cfg_options is not None:
        cfg.merge_from_dict(args.cfg_options)
    # import modules from string list.
    if cfg.get('custom_imports', None):
        from mmcv.utils import import_modules_from_strings
        import_modules_from_strings(**cfg['custom_imports'])

    # import modules from plguin/xx, registry will be updated
    import os
    if hasattr(cfg, 'plugin'):
        if cfg.plugin:
            import importlib
            if hasattr(cfg, 'plugin_dir'):
                plugin_dir = cfg.plugin_dir
                _module_dir = os.path.dirname(plugin_dir)
                _module_dir = _module_dir.split('/')
                _module_path = _module_dir[0]

                for m in _module_dir[1:]:
                    _module_path = _module_path + '.' + m
                print(_module_path)
                plg_lib = importlib.import_module(_module_path)
            else:
                # import dir is the dirpath for the config file
                _module_dir = os.path.dirname(args.config)
                _module_dir = _module_dir.split('/')
                _module_path = _module_dir[0]
                for m in _module_dir[1:]:
                    _module_path = _module_path + '.' + m
                print(_module_path)
                plg_lib = importlib.import_module(_module_path)

    # set cudnn_benchmark
    if cfg.get('cudnn_benchmark', False):
        torch.backends.cudnn.benchmark = True

    cfg.model.pretrained = None
    # in case the test dataset is concatenated
    samples_per_gpu = 1
    if isinstance(cfg.data.test, dict):
        cfg.data.test.test_mode = True
        samples_per_gpu = cfg.data.test.pop('samples_per_gpu', 1)
        if samples_per_gpu > 1:
            # Replace 'ImageToTensor' to 'DefaultFormatBundle'
            cfg.data.test.pipeline = replace_ImageToTensor(
                cfg.data.test.pipeline)
    elif isinstance(cfg.data.test, list):
        for ds_cfg in cfg.data.test:
            ds_cfg.test_mode = True
        samples_per_gpu = max(
            [ds_cfg.pop('samples_per_gpu', 1) for ds_cfg in cfg.data.test])
        if samples_per_gpu > 1:
            for ds_cfg in cfg.data.test:
                ds_cfg.pipeline = replace_ImageToTensor(ds_cfg.pipeline)

    # init distributed env first, since logger depends on the dist info.
    if args.launcher == 'none':
        distributed = False
    else:
        distributed = True
        init_dist(args.launcher, **cfg.dist_params)

    # set random seeds
    if args.seed is not None:
        set_random_seed(args.seed, deterministic=args.deterministic)
    cfg.seed = args.seed
    # build the dataloader
    '''
    dataset = build_dataset(cfg.data.test)
    data_loader = build_dataloader(
        dataset,
        samples_per_gpu=samples_per_gpu,
        workers_per_gpu=cfg.data.workers_per_gpu,
        dist=distributed,
        shuffle=False,
        nonshuffler_sampler=cfg.data.nonshuffler_sampler,
    )
    
    import os

    morai_data_root = "/mnt/ssd_e2e/morai_dataset_final"  # 최상위 디렉토리 경로
    scenario_folders = []

    for dirpath, dirnames, _ in os.walk(morai_data_root):
        if "obj_infos_corr" in dirnames:
            dirnames.remove("obj_infos_corr")  # 특정 폴더 제외

        # "Scenario"를 포함하는 폴더들만 선택
        scenario_folders = [os.path.join(dirpath, dirname) for dirname in dirnames if "Scenario" in dirname]

        break  # 최상위 폴더만 검색

    # breakpoint()
    # print("hihi")
    # parsing Train, Valid, Test  ->  70: 15: 15
    random.seed(2025)  
    train_scenes, temp_folders = train_test_split(scenario_folders, test_size=0.3, random_state=2025)
    val_scenes, test_scenes = train_test_split(temp_folders, test_size=0.5, random_state=2025)

    morai_train_set = MoraiDataset(data_root=morai_data_root, scenes_number=train_scenes)
    morai_val_set = MoraiDataset(data_root=morai_data_root, scenes_number=val_scenes)
    morai_test_set = MoraiDataset(data_root=morai_data_root, scenes_number=test_scenes)

    g_cuda = torch.Generator(device='cpu')
    g_cuda.manual_seed(cfg.seed)
    rank, world_size = get_dist_info()
    # if(distributed == True):
    #     batch_size = cfg.data.samples_per_gpu
    #     num_workers = cfg.data.workers_per_gpu
    # else:
    #     print('WARNING!!!!, Only can be used for obtain inference speed!!!!')
        # sampler = GroupSampler(dataset, cfg.data.samples_per_gpu) if shuffle else None
    batch_size = samples_per_gpu
    num_workers = cfg.data.workers_per_gpu

    init_fn = partial(
        worker_init_fn, num_workers=num_workers, rank=rank,
        seed=cfg.seed) if cfg.seed is not None else None     

    # if(distributed == True):
    #     sampler_train = torch.utils.data.distributed.DistributedSampler(morai_train_set, shuffle=True, num_replicas=world_size, rank=rank)
    #     sampler_val   = torch.utils.data.distributed.DistributedSampler(morai_val_set, shuffle=True, num_replicas=world_size, rank=rank)
    #     dataloader_train = DataLoader(morai_train_set, sampler=sampler_train, batch_size=batch_size, worker_init_fn=init_fn, generator=g_cuda, collate_fn=partial(collate, samples_per_gpu=batch_size), num_workers=num_workers, pin_memory=False)
    #     dataloader_val   = DataLoader(morai_val_set,   sampler=sampler_val,   batch_size=batch_size, worker_init_fn=init_fn, generator=g_cuda, collate_fn=partial(collate, samples_per_gpu=batch_size), num_workers=num_workers, pin_memory=False)
    # else:
    #     dataloader_train = DataLoader(morai_train_set, shuffle=True, batch_size=batch_size, worker_init_fn=init_fn, generator=g_cuda, collate_fn=partial(collate, samples_per_gpu=batch_size), num_workers=num_workers, pin_memory=False)
    dataloader_val = DataLoader(morai_val_set, shuffle=True, batch_size=batch_size, worker_init_fn=init_fn, generator=g_cuda, collate_fn=partial(collate, samples_per_gpu=batch_size), num_workers=num_workers, pin_memory=False)


    data_loader = dataloader_val 
    '''


    ###########################














    # build the model and load checkpoint
    cfg.model.train_cfg = None
    model = build_model(cfg.model, test_cfg=cfg.get('test_cfg'))
    fp16_cfg = cfg.get('fp16', None)
    if fp16_cfg is not None:
        wrap_fp16_model(model)
    checkpoint = load_checkpoint(model, args.checkpoint, map_location='cpu')
    if args.fuse_conv_bn:
        model = fuse_conv_bn(model)
    # old versions did not save class info in checkpoints, this walkaround is
    # for backward compatibility
    if 'CLASSES' in checkpoint.get('meta', {}):
        model.CLASSES = checkpoint['meta']['CLASSES']
    else:
        model.CLASSES = dataset.CLASSES
    # palette for visualization in segmentation tasks
    if 'PALETTE' in checkpoint.get('meta', {}):
        model.PALETTE = checkpoint['meta']['PALETTE']
    elif hasattr(dataset, 'PALETTE'):
        # segmentation dataset has `PALETTE` attribute
        model.PALETTE = dataset.PALETTE

    if not distributed:
        # assert False
        model = MMDataParallel(model, device_ids=[0])
        # outputs = single_gpu_test(model, data_loader, args.show, args.show_dir)
    # else:
    #     model = MMDistributedDataParallel(
    #         model.cuda(),
    #         device_ids=[torch.cuda.current_device()],
    #         broadcast_buffers=False)
    #     outputs = custom_multi_gpu_test(model, data_loader, args.tmpdir,
    #                                     args.gpu_collect)

    """
    tmp = {}
    tmp['bbox_results'] = outputs
    outputs = tmp
    rank, _ = get_dist_info()
    if rank == 0:
        if args.out:
            print(f'\nwriting results to {args.out}')
            # assert False
            if isinstance(outputs, list):
                mmcv.dump(outputs, args.out)
            else:
                mmcv.dump(outputs['bbox_results'], args.out)
        kwargs = {} if args.eval_options is None else args.eval_options
        kwargs['jsonfile_prefix'] = osp.join('test', args.config.split(
            '/')[-1].split('.')[-2], time.ctime().replace(' ', '_').replace(':', '_'))
        if args.format_only:
            dataset.format_results(outputs['bbox_results'], **kwargs)

        if args.eval:
            eval_kwargs = cfg.get('evaluation', {}).copy()
            # hard-code way to remove EvalHook args
            for key in [
                    'interval', 'tmpdir', 'start', 'gpu_collect', 'save_best',
                    'rule'
            ]:
                eval_kwargs.pop(key, None)
            eval_kwargs.update(dict(metric=args.eval, **kwargs))

            print(dataset.evaluate(outputs['bbox_results'], **eval_kwargs))
    
        # # # NOTE: record to json
        # json_path = args.json_dir
        # if not os.path.exists(json_path):
        #     os.makedirs(json_path)
        
        # metric_all = []
        # for res in outputs['bbox_results']:
        #     for k in res['metric_results'].keys():
        #         if type(res['metric_results'][k]) is np.ndarray:
        #             res['metric_results'][k] = res['metric_results'][k].tolist()
        #     metric_all.append(res['metric_results'])
        
        # print('start saving to json done')
        # with open(json_path+'/metric_record.json', "w", encoding="utf-8") as f2:
        #     json.dump(metric_all, f2, indent=4)
        # print('save to json done')
    """
    
    return model