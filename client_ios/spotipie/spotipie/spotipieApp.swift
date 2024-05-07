//
//  spotipieApp.swift
//  spotipie
//
//  Created by Sudhip Nashi on 7/12/23.
//

import SwiftUI
import AVFAudio

@main
struct spotipieApp: App {
    init() {
        try? AVAudioSession.sharedInstance().setCategory(.playback)
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onAppear {
                    print(URLCache.shared.currentDiskUsage)
                }
        }
    }
}
