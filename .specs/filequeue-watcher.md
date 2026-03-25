Filequeue-watcher

- program watches a directory {dir}
- when a new file arrives is calls "file-queue -dequeue --directory {dir}"
- Capture the output of the command and pipes it to "file-processor" program
