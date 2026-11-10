import Foundation
import Vision

var outputs: [[String: Any]] = []
for path in CommandLine.arguments.dropFirst() {
    let request = VNDetectBarcodesRequest()
    request.symbologies = [.qr]
    let handler = VNImageRequestHandler(url: URL(fileURLWithPath: path))
    do {
        try handler.perform([request])
        let decoded = (request.results ?? []).compactMap { $0.payloadStringValue }
        outputs.append(["image": path, "decoded_urls": decoded])
    } catch {
        outputs.append(["image": path, "error": String(describing: error)])
    }
}
let data = try JSONSerialization.data(withJSONObject: outputs, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write(Data([10]))
