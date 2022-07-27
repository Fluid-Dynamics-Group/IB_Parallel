import distribute_compute_config as distribute
import os

class Config:
    def __init__(
        self,
        istart: int,
        istop: int,
        isave: int,
        irestart: int,
        m: int,
        n: int,
        dt: float,
        re: float,
        fsi_tol: float,
        atol: float,
        rtol: float,
        len: float,
        offsetx: float,
        offsety: float,
        mgridlev: float,
        compute_pressure: str,
        dimen: int,
        num_stat: str,
        motion_prescribed: str,
        sub_domain: str,
        sub_domainfull_rectangular: str,
        sub_domain_precomputed: str,
        sdxi: float,
        sdxe: float,
        sdyi: float,
        sdye: float,
        delta_sd: float,
    ):
        self.istart                    = istart
        self.istop                     = istop
        self.isave                     = isave
        self.irestart                  = irestart
        self.m                         = m
        self.n                         = n
        self.dt                        = dt
        self.re                        = re
        self.fsi_tol                   = fsi_tol
        self.atol                      = atol
        self.rtol                      = rtol
        self.len                       = len
        self.offsetx                   = offsetx
        self.offsety                   = offsety
        self.mgridlev                  = mgridlev
        self.compute_pressure          = compute_pressure
        self.dimen                     = dimen
        self.num_stat                  = num_stat
        self.motion_prescribed         = motion_prescribed
        self.sub_domain                = sub_domain
        self.sub_domainfull_rectangular= sub_domainfull_rectangular
        self.sub_domain_precomputed    = sub_domain_precomputed
        self.sdxi                      = sdxi
        self.sdxe                      = sdxe
        self.sdyi                      = sdyi
        self.sdye                      = sdye
        self.delta_sd                  = delta_sd


    def to_string(self):

        out = \
f"""&READ_PARAMETERS     
ISTART = {self.istart}, 
ISTOP =  {self.istop}, 
ISAVE =  {self.isave},
IRESTART = {self.irestart}, 
M =      {self.m}, 
N =      {self.n}, 
DT =     {self.dt}, 
Re =     {self.re}, 
FSI_TOL = {self.fsi_tol},
ATOL = {self.atol},
RTOL = {self.rtol},
LEN =    {self.len}, 
OFFSETX =  {self.offsetx}, 
OFFSETY =  {self.offsety}, 
MGRIDLEV =  {self.mgridlev}, 
COMPUTE_PRESSURE = {self.compute_pressure}, 
dimen = {self.dimen},
num_stat={self.num_stat},
motion_prescribed={self.motion_prescribed},
sub_domain = {self.sub_domain},
sub_domain_full_rectangular = {self.sub_domainfull_rectangular},
sub_domain_precomputed = {self.sub_domain_precomputed},
sdxi = {self.sdxi},
sdxe = {self.sdxe},
sdyi = {self.sdyi},
sdye = {self.sdye},
delta_sd = {self.delta_sd}
/                    
"""
        return out

    def to_file(self, path: str):
        with open(path, "w") as f:
            f.write(self.to_string())

    @staticmethod
    def default():
        return Config(
            istart = 0,
            istop = 10,
            isave = 10,
            irestart = 0,
            m = 860,
            n = 860,
            dt = 0.0004375,
            re = 1000.,
            fsi_tol = 1e-7,
            atol = 1e-7,
            rtol = 1e-7,
            len = 3.,
            offsetx = 0.5,
            offsety = 1.5,
            mgridlev=5,
            compute_pressure="T",
            dimen = 2,
            num_stat = "F",
            motion_prescribed="F",
            sub_domain="T",
            sub_domainfull_rectangular="F",
            sub_domain_precomputed="F",
            sdxi = 0.225581395348837,
            sdxe = 0.696511627906977,
            sdyi = -0.233720930232558,
            sdye = 0.094186046511628,
            delta_sd =  0.003488372093023
        )

def change_reynolds_number(re: float):
    config = Config.default()
    config.re = re

    return config

class ConfigWrapper():
    def __init__(self, config: Config, name: str):
        self.config = config
        self.name = name


def main():

    re_values = [40., 200., 400., 1000.]

    configs = []

    for re in re_values:
        config = change_reynolds_number(re)

        name = f"reynolds_{int(re)}"
        wrapper = ConfigWrapper(config, name)

        configs.append(wrapper)

    namespace = "aditya_ibparallel"
    batch_name = "reynolds_sweep_1"

    output_folder = f"./distribute/{batch_name}"

    if os.path.exists(output_folder):
        raise ValueError("batch already exists!")
    else:
        os.mkdir(output_folder)

    caps = ["apptainer"]
    meta = distribute.metadata(namespace, batch_name, caps, matrix_username = "@adinair:matrix.org")

    cwd = os.getcwd()

    sif_path = cwd + "/ib_parallel.sif"
    required_files = []

    #
    # files that are present for ALL jobs
    #
    for file_name in ["body.001.inp", "body.002.inp", "sd_precomputed.chd"]:
        path = cwd + "/input/" + file_name 
        file = distribute.file(path)

        required_files.append(file)

    required_mounts = [
        "/IB_Parallel/input/",
        "/IB_Parallel/output/"
    ]
    init = distribute.initialize(sif_path, required_files, required_mounts)

    jobs = []

    for config_wrapper in configs:
        config_file_path = cwd + f"/{output_folder}/" + config_wrapper.name + ".inp"

        config_wrapper.config.to_file(config_file_path)

        # if this is aditya txt then
        #file2 = distribute.file("./path/to/file.aditya.txt", alias = "ib.inp")
        config_file = distribute.file(config_file_path, alias = "ib.inp")

        # files that are presnet for ONLY this job
        required_files = [config_file]
        job = distribute.job(config_wrapper.name, required_files)

        jobs.append(job)

    description = distribute.description(init, jobs)
    
    config = distribute.apptainer_config(meta, description)

    distribute.write_config_to_file(config, f"{output_folder}/distribute-jobs.yaml")


if __name__ == "__main__":
    main()
