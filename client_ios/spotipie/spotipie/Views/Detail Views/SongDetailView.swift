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
                    
                if let album = song.album, let name = song.album?.name {
                    HStack {
                        NavigationLink{
                            AlbumDetailView(album: album)
                        } label: {
                            Text("\(name)")
                                .font(Font.system(size: 20, weight: .bold, design: .rounded))
                                .lineLimit(1)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .minimumScaleFactor(0.2)
                        }
                    }
                    .padding(.bottom, 10)
                }

                if let duration_ms = song.duration_ms {
                    let duration = TimeInterval(duration_ms/1000)
                    Text("Duration: \(duration.minuteSecond)")
                        .frame(maxWidth: /*@START_MENU_TOKEN@*/.infinity/*@END_MENU_TOKEN@*/, alignment: .leading)
                        .font(.subheadline)
                }
                
                if let predicted_genres = song.predicted_genres {
                    if predicted_genres.count != 0 {
                        let predicted_genres_string = predicted_genres.joined(separator: ", ")
                        Text("Predicted Genres: \(predicted_genres_string)")
                            .frame(maxWidth: /*@START_MENU_TOKEN@*/.infinity/*@END_MENU_TOKEN@*/, alignment: .leading)
                            .font(.subheadline)
                    }
                }
                
                if let release_date = song.album?.release_date {
                    Text("Released: \(release_date)")
                        .frame(maxWidth: /*@START_MENU_TOKEN@*/.infinity/*@END_MENU_TOKEN@*/, alignment: .leading)
                        .font(.subheadline)
                }
                
                if let play_count = song.play_count {
                    Text("Play Count: \(play_count)")
                        .frame(maxWidth: /*@START_MENU_TOKEN@*/.infinity/*@END_MENU_TOKEN@*/, alignment: .leading)
                        .font(.subheadline)
                }
            }
            .frame(width:frameBounding?.width)
        }.onAppear {
            Task {
                try await song.load(base_url: url)
                
                if var album = song.album {
                    try await album.load(base_url: url)
                }
            }
        }.environment(\EnvironmentValues.refresh as! WritableKeyPath<EnvironmentValues, RefreshAction?>, nil)
    }
}

