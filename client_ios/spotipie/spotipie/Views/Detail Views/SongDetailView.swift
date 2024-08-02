//
//  SongDetail.swift
//  spotipie
//
//  Created by Sudhip Nashi on 5/5/24.
//

import SwiftUI
import Kingfisher
import AVFoundation

struct SongDetailView: View {
    @State var song: Song
    @State var playingPreview = false
    @State var player: AVPlayer?
    @State var frameBounding: CGSize?
    @AppStorage("remote_url") var url: URL = URL(string: DEFAULT_URL)!
    
    var body: some View {
        ScrollView {
                KFImage(song.album?.images?[0].url)
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: 300)
                    .cornerRadius(20)
                    .background (
                        GeometryReader { geometry in
                            Color.clear.onAppear {
                                frameBounding = geometry.size
                            }
                        }
                    )
            
            VStack {
                HStack {
                    // ew
                    Text((song.name ?? "Loading") + ((song.explicit ?? false) == true ? " 🅴" : ""))
                        .font(Font.system(size: 40, weight: .bold, design: .rounded))
                        .minimumScaleFactor(0.2)
                        .lineLimit(1)

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

                if let duration_ms = song.duration_ms {
                    let duration = TimeInterval(duration_ms/1000)
                    Text("Duration: " + duration.minuteSecond)
                        .frame(maxWidth: /*@START_MENU_TOKEN@*/.infinity/*@END_MENU_TOKEN@*/, alignment: .leading)
                        .font(.subheadline)
                }

                Spacer()
            }
            .frame(width:frameBounding?.width)
        }.onAppear {
            Task {
                try await song.load(base_url: url)
            }
        }.environment(\EnvironmentValues.refresh as! WritableKeyPath<EnvironmentValues, RefreshAction?>, nil)
    }
}

