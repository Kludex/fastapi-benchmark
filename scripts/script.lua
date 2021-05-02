wrk.method = "GET"
wrk.headers["content-type"] = "application/json"

name = os.getenv("NAME")
filename = os.getenv("FILENAME")


done = function(summary, latency, requests)
    file = assert(io.open(filename, "a"))
    file.write(
        file,
        string.format(
            "%s,%d,%.2f,%.2f,%.2f,%.2f,%d,%d,%d\n",
            name,
            summary.requests,
            latency:percentile(50) / 1000,
            latency:percentile(75) / 1000,
            latency:percentile(90) / 1000,
            latency.mean / 1000,
            summary.errors.status,
            summary.errors.read,
            summary.errors.timeout
            ));
    file.close()
end
