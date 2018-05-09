from app import jobs
job = jobs()
if not job.ok:
    print(job.text)
else:
    import pdb; pdb.set_trace()
    print()
