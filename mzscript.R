args <- commandArgs(TRUE)

mzPlotter::createReport(readPath = args[1],
                        args[2])