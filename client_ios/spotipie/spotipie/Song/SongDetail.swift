//
//  SongDetail.swift
//  spotipie
//
//  Created by Sudhip Nashi on 5/5/24.
//

import SwiftUI
import AVFoundation

struct SongDetail: View {
    @State var song: Song
    @State var player: AVPlayer?
    
    var body: some View {
        VStack {
            Text(song.song_details?.name ?? "Unknown")
            Button("Play") {
                if let song_details = song.song_details {
                    let playerItem = AVPlayerItem(url:song_details.preview_url)
                    self.player = AVPlayer(playerItem: playerItem)
                    self.player?.play()
                }
                
            }
        }.onAppear {
            Task {
                try await song.load()
            }
        }
    }
}

