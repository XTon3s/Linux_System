import csv
import subprocess
import os
import re
from urllib.parse import urlparse
from pathlib import Path
import shutil


DOCKER_IMAGE = "debian:latest"
TIMEOUT_SECONDS = 300
WORKSPACE_DIR = "grading_workspace"


def sanitize_name(name: str) -> str:
    return re.sub(r'[^a-z0-9\-]', '', name.lower())


def prepare_student_workspace(name: str) -> Path:
    student_dir = Path(WORKSPACE_DIR) / sanitize_name(name)
    if student_dir.exists():
        shutil.rmtree(student_dir)
    student_dir.mkdir(parents=True)
    return student_dir


def build_image_with_script(name: str, repo_url: str, script_path: str, image_tag: str):
    student_dir = prepare_student_workspace(name)

    # git clone
    repo_clone_dir = student_dir / "repo"
    clone_result = subprocess.run(
        ["git", "clone", repo_url, str(repo_clone_dir)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if clone_result.returncode != 0:
        raise RuntimeError(f"git clone 실패: {clone_result.stderr.strip()}")

    full_script_path = repo_clone_dir / script_path
    if not full_script_path.exists():
        raise FileNotFoundError(f"스크립트 파일이 존재하지 않음: {full_script_path}")

    # Dockerfile 작성
    dockerfile_path = student_dir / "Dockerfile"
    relative_script_inside_image = "/tmp/script.sh"
    dockerfile_content = f"""FROM {DOCKER_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y curl git build-essential libssl-dev zlib1g-dev \\
    libbz2-dev libreadline-dev libsqlite3-dev wget llvm libncursesw5-dev xz-utils tk-dev \\
    libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev ca-certificates

# pyenv 환경 변수 설정
ENV PYENV_ROOT=$HOME/.pyenv
ENV PATH=$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

COPY repo/{script_path} {relative_script_inside_image}
RUN chmod +x {relative_script_inside_image} && bash {relative_script_inside_image}"""

    dockerfile_path.write_text(dockerfile_content)

    # docker build
    subprocess.run(
        ["docker", "build", "-t", image_tag, str(student_dir)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=TIMEOUT_SECONDS
    )

def run_check(image_tag: str):
    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm", image_tag,
                "bash", "-c", "pyenv -v && python --version"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60
        )
        output = result.stdout
        success = "pyenv" in output and "3.12" in output
        return success, output
    except Exception as e:
        return False, f"실행 중 예외: {e}"


def grade_submissions(submission_file: str, result_file: str = "results.csv"):
    Path(WORKSPACE_DIR).mkdir(exist_ok=True)

    results = []

    with open(submission_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) != 4:
                print(f"❗ 잘못된 행 형식: {row}")
                continue
            name, repo_url, script_dir, script_file = map(str.strip, row)
            print(f"▶️ 채점 중: {name}")

            try:
                script_rel_path = os.path.join(script_dir, script_file)
                image_tag = f"pyenv-grader-{sanitize_name(name)}"

                build_image_with_script(name, repo_url, script_rel_path, image_tag)
                success, log = run_check(image_tag)

                score = 100 if success else 70
                results.append([name, repo_url, script_rel_path, score, "정상" if success else "오류", log.strip()[:300]])

            except Exception as e:
                results.append([name, repo_url, f"{script_dir}/{script_file}", 70, "실패", str(e)])
            finally:
                subprocess.run(["docker", "rmi", "-f", image_tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with open(result_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["이름", "레포지토리", "스크립트경로", "점수", "결과", "로그요약"])
        writer.writerows(results)

    print(f"✅ 채점 완료: {result_file} 생성됨")


if __name__ == "__main__":
    grade_submissions("submissions.txt")
