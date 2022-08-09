# result = subprocess.check_output(["python ../scrapers/poryadok.py https://spb.poryadok.ru/catalog/osvezhiteli_vozdukha/ 511002883"])
# print(result)
# from subprocess import Popen, PIPE
#
# p = Popen(['program', 'arg1'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
# output, err = p.communicate("python ../scrapers/poryadok.py https://spb.poryadok.ru/catalog/osvezhiteli_vozdukha/ 511002883")
# print(output)

# from subprocess import check_output
# out = check_output("python ../scrapers/poryadok.py https://spb.poryadok.ru/catalog/osvezhiteli_vozdukha/ 511002883")
# print(str(out).strip())

from subprocess import PIPE, Popen

command = "python ../scrapers/maxidom.py https://www.maxidom.ru/catalog/osvezhiteli-vozduha/ 511002883"
with Popen(command, stdout=PIPE, stderr=None, shell=True) as process:
    result = process.communicate()[0].decode("utf-8")
    print(result)
