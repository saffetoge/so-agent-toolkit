import AppKit

// Kullanım: airdrop <dosya>... AirDrop penceresini açar, cihazı kullanıcı seçer.
let dosyalar = CommandLine.arguments.dropFirst().map { URL(fileURLWithPath: $0) }

final class Temsilci: NSObject, NSSharingServiceDelegate {
    func sharingService(_ servis: NSSharingService, didShareItems items: [Any]) {
        print("AirDrop: gönderildi")
        exit(0)
    }

    func sharingService(_ servis: NSSharingService, didFailToShareItems items: [Any], error: Error) {
        print("AirDrop: gönderilmedi (\(error.localizedDescription))")
        exit(1)
    }
}

let uygulama = NSApplication.shared
uygulama.setActivationPolicy(.accessory)

guard !dosyalar.isEmpty,
      let servis = NSSharingService(named: .sendViaAirDrop),
      servis.canPerform(withItems: dosyalar) else {
    print("AirDrop kullanılamıyor (dosya yok ya da Wi-Fi/Bluetooth kapalı)")
    exit(1)
}

let temsilci = Temsilci()
servis.delegate = temsilci
uygulama.activate(ignoringOtherApps: true)
servis.perform(withItems: dosyalar)
uygulama.run()
