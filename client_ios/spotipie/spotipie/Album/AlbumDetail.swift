//
//  SongDetail.swift
//  spotipie
//
//  Created by Sudhip Nashi on 5/5/24.
//

import SwiftUI
import Kingfisher
import AVFoundation

struct AlbumDetail: View {
    @State var album: Album
    @State var playingPreview = false
    @State var frameBounding: CGSize?
    
    var body: some View {
        GeometryReader { reader in
            ScrollView {
                KFImage(album.images?[0].url)
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
                    VStack {
                        HStack {
                            Text(album.name ?? "Loading")
                                .font(Font.system(size: 40, weight: .bold, design: .rounded))
                                .minimumScaleFactor(0.2)
                                .lineLimit(1)
                            
                            Spacer()
                        }
                        
                        Spacer()
                        
                        Text("Release Date: " + (album.release_date ?? "Loading"))
                            .frame(maxWidth: /*@START_MENU_TOKEN@*/.infinity/*@END_MENU_TOKEN@*/, alignment: .leading)
                            .font(.subheadline)
                        
                        Text("Label: " + (album.label ?? "Loading"))
                            .frame(maxWidth: /*@START_MENU_TOKEN@*/.infinity/*@END_MENU_TOKEN@*/, alignment: .leading)
                            .font(.subheadline)
                    }
                    .frame(width:frameBounding?.width, alignment: .center)

                    List  {
                        Section(String(album.total_tracks ?? 0) + " Tracks") {
                            if let tracks = album.tracks?.items {
                                ForEach(tracks, id: \.name) { song in
                                    NavigationLink {
                                        SongDetail(song: Song(id: song.id))
                                    } label: {
                                        SongCell(name: song.name)
                                    }
                                }
                            }
                        }
                    }.frame(width: reader.size.width, height: reader.size.height, alignment: .center)
                        .scrollContentBackground(.hidden)
                    
                    Spacer()
                }
            }.onAppear {
                Task {
                    try await album.load()
                }
            }
        }
    }
}

