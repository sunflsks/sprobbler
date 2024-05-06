//
//  SongDetail.swift
//  spotipie
//
//  Created by Sudhip Nashi on 5/5/24.
//

import SwiftUI
import Kingfisher
import AVFoundation

struct SongDetail: View {
    @State var song: Song
    @State var playingPreview = false
    @State var player: AVPlayer?
    
    var body: some View {
        ScrollView {
            KFImage(song.album?.images?[0].url)
                .resizable()
                .scaledToFit()
                .frame(height: 300)
                .cornerRadius(20)
            VStack {
                Text(song.name ?? "Loading")
                    .font(Font.system(size: 40, weight: .bold, design: .rounded))
                Spacer()
                if let duration_ms = song.duration_ms {
                    let duration = TimeInterval(duration_ms/1000)
                    Text(duration.minuteSecond)
                }
                Spacer()
                Image(systemName: playingPreview ? "pause.circle.fill": "play.circle.fill")
                    .font(.system(size: 50))
                    .onTapGesture {
                        playingPreview.toggle()
                        if let preview_url = song.preview_url {
                            if (player == nil) { player = AVPlayer(url: preview_url) }
                            
                            if playingPreview {
                                player?.play()
                            } else {
                                player?.pause()
                            }
                        }
                    }
            }
        }.onAppear {
            Task {
                try await song.load()
            }
        }
    }
}

