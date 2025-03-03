
import xarray as xr
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from matplotlib import patches
from PIL import Image
import glob
import cartopy.crs as ccrs
from   cartopy.mpl.ticker import LongitudeFormatter,LatitudeFormatter
from scipy import stats
from matplotlib.colors import LinearSegmentedColormap
# 
def plot_lagcorr(x, y, title, xlabel='Lag[mon]', ylabel='Correlation',
                 fsize_label=18, fsize_title=28, fsize_tick=14,
                 savefig=False, fname="./sample.png"):
    fig = plt.figure(figsize=(6.4,4.8))
    ax = fig.add_subplot()
    ax.plot(x, y, linewidth=2)
    ax.set_xlim(min(x), max(x))
    ax.set_ylim(-1,1)
    ax.hlines([0], min(x), max(x), linewidth=2, color='black')
    ax.vlines([0], -1, 1, linewidth=2, color='black')
    ax.set_title(title, fontsize=fsize_title)
    ax.set_xlabel(xlabel, fontsize=fsize_label)
    ax.set_ylabel(ylabel, fontsize=fsize_label)
    ax.tick_params('x', labelsize=fsize_tick)
    ax.tick_params('y', labelsize=fsize_tick)
    ax.grid()
    if savefig:
        
        fig.savefig(fname)
# 
def plot_1d_normalized_series(series, key, title, ylabel='Index /std', xlabel='Time[year]',
                           yr_start=1979, yr_end=2018, yr_int=10,
                           fsize_label=18, fsize_title=28, fsize_tick=14,
                           savefig=False, fname="./sample.png"):
    fig = plt.figure(figsize=(6.4,4.8))
    ax = fig.add_subplot()
    ax.plot(series[key],series.values)
    x_min = dt.datetime(yr_start-5,1,1)
    x_max = dt.datetime(yr_end+5,1,1)
    #xticks_data = np.array([cft.DatetimeGregorian(yr,1,1) for yr in range(x_min,x_max,yr_int)])
    ax.set_xlim((x_min,x_max))
    #abs_max = max(np.abs(series.values.min()), np.abs(series.values.max()))
    #ax.set_ylim(-abs_max-0.5, abs_max+0.5)
    ax.hlines([0], x_min, x_max, linewidth=2, color='black')
    ax.set_xlabel(xlabel, fontsize=fsize_label)
    ax.set_ylabel(ylabel, fontsize=fsize_label)
    ax.xaxis.set_major_locator(mdates.YearLocator(yr_int,1,1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params('x', labelsize=fsize_tick)
    ax.tick_params('y', labelsize=fsize_tick)
    ax.set_title(title, fontsize=fsize_title)
    ax.grid()
    if savefig:
        
        fig.savefig(fname)
#
def create_gif(fname_in,duration=150, loop=0, fname_save='./image.gif'):
    path_list = sorted(glob.glob(fname_in)) # ファイルパスをソートしてリストする
    imgs = []                                                   # 画像をappendするための空配列を定義
 
    # ファイルのフルパスからファイル名と拡張子を抽出
    for i in range(len(path_list)):
        img = Image.open(path_list[i])                          # 画像ファイルを1つずつ開く
        imgs.append(img)                                        # 画像をappendで配列に格納していく
 
    # appendした画像配列をGIFにする。durationで持続時間、loopでループ数を指定可能。
    imgs[0].save(fname_save,
                 save_all=True, append_images=imgs[1:], optimize=True, duration=duration, loop=loop)
# 
def draw_hrz_field(field,
                   clev_min=None,clev_max=None,clev_int=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",
                   contour=False,grid=False,grid_width=1.,
                   rec=False,
                   xy=None,width=None,height=None,
                   landcol=True,landfc="beige",
                   savefig=False,fname_save=None):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # Figure/Axes objects
    fig = plt.figure(figsize=(6,4),dpi=150,layout='constrained') # 図のサイズと解像度を指定
    ax = fig.add_subplot(projection=ccrs.PlateCarree(central_longitude=180)) # cartopyのprojectionを指定したAxesオブジェクトを生成

    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
        cticks = None
    elif clev_min is not None and clev_max is not None and clev_int == None:
        nlev = 12
        clevels = np.linspace(clev_min,clev_max,nlev)
        cticks = list(clevels[:nlev//2:2])+list(clevels[nlev//2+1::2])#np.linspace(clev_min,clev_max,7)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks = None
    else:
        raise Exception("Color level max/min/int is not correct!")

    # Plot
    field.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels,
        cmap=cmap,
        extend='both',
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1.,"aspect":40,'ticks':cticks,},
    ) # xarrayに内蔵されたplot.contourfメソッド。
    # subarc/subtro front領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)

    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=3)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),
                     linestyle="--",linewidth=grid_width,
                     draw_labels=False,
                     alpha=0.8,
                     zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=2)
    # save figure
    if savefig: 
        fig.savefig(fname_save)

# 
def axplot_hrz_field(ax,field,
                   clev_min=None,clev_max=None,clev_int=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",add_colorbar=False,cout=True,
                   grid=False,grid_width=1.,
                   rec=False,
                   xy=None,width=None,height=None,
                   landcol=True,landfc="beige",):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
        cticks = None
    elif clev_min is not None and clev_max is not None and clev_int == None:
        nlev = 12
        clevels = np.linspace(clev_min,clev_max,nlev)
        cticks = list(clevels[:nlev//2:2])+list(clevels[nlev//2+1::2])#np.linspace(clev_min,clev_max,7)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks = None
    else:
        raise Exception("Color level max/min/int is not correct!")

   # Plot
    if add_colorbar:
        c=field.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1.1,"aspect":40,'ticks':cticks},)
    else:
        c=field.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,)
    # subarc/subtro front領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)

    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=3)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),
                     linestyle="--",linewidth=grid_width,
                     draw_labels=False,
                     alpha=0.8,
                     zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=2)
    if cout:
        return c

def axplot_hrz_field_hatch(ax,field,field_hatch,
                   clev_min=None,clev_max=None,clev_int=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",add_colorbar=False,cout=True,
                   grid=False,grid_width=1.,hatches=[".."],echatch="black",
                   rec=False,
                   xy=None,width=None,height=None,
                   landcol=True,landfc="lightgray",):
    
    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
        cticks = None
    elif clev_min is not None and clev_max is not None and clev_int == None:
        nlev = 12
        clevels = np.linspace(clev_min,clev_max,nlev)
        cticks = list(clevels[:nlev//2:2])+list(clevels[nlev//2+1::2])#np.linspace(clev_min,clev_max,7)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks = None
    else:
        raise Exception("Color level max/min/int is not correct!")

   # Plot
    if add_colorbar:
        c=field.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1.1,"aspect":40,'ticks':cticks},)
    else:
        c=field.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,)
    # Hatching
    ax_addhatch(ax,field_hatch.lon.values,field_hatch.lat.values,field_hatch,
    hatches=hatches,ec=echatch)
    
    # subarc/subtro front領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)

    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=3)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),
                     linestyle="--",linewidth=grid_width,
                     draw_labels=False,
                     alpha=0.8,
                     zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=2)
    if cout:
        return c

def axplot_polar_field_hatch(ax,field,field_hatch,
                   clev_min=None,clev_max=None,clev_int=None,
                   var_label="",title="",
                   cmap="RdBu_r",add_colorbar=False,cout=True,
                   grid=False,grid_width=1.,hatches=[".."],echatch="black",
                   rec=False,
                   xy=None,width=None,height=None,
                   landcol=True,landfc="beige",):
    
    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
        cticks = None
    elif clev_min is not None and clev_max is not None and clev_int == None:
        nlev = 12
        clevels = np.linspace(clev_min,clev_max,nlev)
        cticks = list(clevels[:nlev//2:2])+list(clevels[nlev//2+1::2])#np.linspace(clev_min,clev_max,7)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks = None
    else:
        raise Exception("Color level max/min/int is not correct!")

   # Plot
    if add_colorbar:
        c=field.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1.1,"aspect":40,'ticks':cticks},)
    else:
        c=field.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,)
    # Hatching
    ax_addhatch(ax,field_hatch.lon.values,field_hatch.lat.values,field_hatch,
    hatches=hatches,ec=echatch)
    
    # subarc/subtro front領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)

    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    # xticks = np.arange(0,360,xtickint)
    # yticks = np.arange(-80,90,ytickint)
    # ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    # ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    # ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=3)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),
                     linestyle="--",linewidth=grid_width,
                     draw_labels=False,
                     alpha=0.8,
                     zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=2)
    if cout:
        return c

def axplot_hrz_field_double(ax,field1, field2,
                   clev_min1=None,clev_max1=None,clev_int1=None,
                   clev_min2=None,clev_max2=None,clev_int2=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",add_colorbar=False,cout=True,ccontour='black',
                   clabel=False,clabelsize='medium',cclabel="black",inline_spacing=5,grid=False,grid_width=1.,contourwidth=1,
                   sub_contour=False,
                   fmt='%.1f',
                   rec=False,xy=None,width=None,height=None,
                   landcol=True,landfc="beige",zland=5,zcontour=6.2,):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # カラーバーの範囲の指定
    if clev_min1 is not None and clev_max1 is not None and clev_int1 is not None:
        clevels1 = np.arange(clev_min1,clev_max1+clev_int1/2,clev_int1)
        cticks1 = None
    elif clev_min1 is not None and clev_max1 is not None and clev_int1 == None:
        nlev = 12
        clevels1 = np.linspace(clev_min1,clev_max1,nlev)
        cticks1 = list(clevels1[:nlev//2:2])+list(clevels1[nlev//2+1::2])
    elif (clev_min1,clev_max1,clev_int1)==(None,None,None):
        clevels1 = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks1 = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    # field2のコンターレベルの指定
    if clev_min2 is not None and clev_max2 is not None and clev_int2 is not None:
        clevels2 = np.arange(clev_min2,clev_max2+clev_int2,clev_int2)
    elif (clev_min2,clev_max2,clev_int2)==(None,None,None):
        clevels2 = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # field2の副コンター、細い線
    clev_int2_sub = clev_int2/5
    if clev_min2 is not None and clev_max2 is not None and clev_int2_sub is not None:
        clevels2_sub = np.arange(clev_min2,clev_max2+clev_int2_sub,clev_int2_sub)
    elif (clev_min2,clev_max2,clev_int2_sub)==(None,None,None):
        clevels2_sub = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # Plot
    if add_colorbar:
        c=field1.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels1,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1,"aspect":40,'ticks':cticks1},)
    else:
        c=field1.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels1,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,)
    # field2はコンター
    contour = field2.plot.contour(
        ax=ax,
        transform=ccrs.PlateCarree(),
        levels=clevels2,
        linewidths=contourwidth,
        # linestyles=['-','--','--','--','--'],
        colors=ccontour,zorder=zcontour,
    )
    # コンターのラベルの作成
    if clabel:
        ax.clabel(
            contour,
            fmt=fmt,
            fontsize=clabelsize,inline_spacing=inline_spacing,
            colors=cclabel,
            zorder=6.1
        )
    # sub_contour
    if sub_contour:
        field2.plot.contour(
            ax=ax,
            transform=ccrs.PlateCarree(),
            levels=clevels2_sub,
            linewidths=0.2,
            colors=ccontour,
            linestyles='--',
            add_labels=False,
            zorder=6
        )
    
    # 指定領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)
    
    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=10)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
        draw_labels=False,
        alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=zland)

    if cout:
        return c

def axplot_hrz_field_contour(ax,field,
                   clev_min=None,clev_max=None,clev_int=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cout=False,ccontour='black',
                   clabel=False,clabelsize='medium',cclabel="black",inline_spacing=7,grid=False,grid_width=1.,contourwidth=1,
                   sub_contour=False,
                   fmt='%.1f',
                   rec=False,xy=None,width=None,height=None,
                   landcol=True,landfc="beige",zland=5,zcontour=6.2,):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # fieldのコンターレベルの指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int,clev_int)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # fieldの副コンター、細い線
    clev_int_sub = clev_int/5
    if clev_min is not None and clev_max is not None and clev_int_sub is not None:
        clevels_sub = np.arange(clev_min,clev_max+clev_int_sub,clev_int_sub)
    elif (clev_min,clev_max,clev_int_sub)==(None,None,None):
        clevels_sub = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    
    # fieldはコンター
    contour = field.plot.contour(
        ax=ax,
        transform=ccrs.PlateCarree(),
        levels=clevels,
        linewidths=contourwidth,
        # linestyles=['-','--','--','--','--'],
        colors=ccontour,zorder=zcontour,
    )
    # コンターのラベルの作成
    if clabel:
        ax.clabel(
            contour,
            fmt=fmt,
            fontsize=clabelsize,inline_spacing=inline_spacing,
            colors=cclabel,
            zorder=6.1
        )
        
    # sub_contour
    if sub_contour:
        field.plot.contour(
            ax=ax,
            transform=ccrs.PlateCarree(),
            levels=clevels_sub,
            linewidths=0.2,
            colors=ccontour,
            linestyles='--',
            add_labels=False,
            zorder=6
        )
    
    # 指定領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)
    
    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=10)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
        draw_labels=False,
        alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=zland)

    if cout:
        return contour



def axplot_hrz_field_double_hatch(ax,field1, field2, field_hatch,
                   clev_min1=None,clev_max1=None,clev_int1=None,
                   clev_min2=None,clev_max2=None,clev_int2=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",add_colorbar=False,cout=True,ccontour='black',
                   clabel=False,clabelsize='medium',cclabel="black",inline_spacing=5,grid=False,grid_width=1.,contourwidth=1,
                   sub_contour=False,hatches=[".."],echatch="black",
                   fmt='%.1f',
                   rec=False,xy=None,width=None,height=None,
                   landcol=True,landfc="beige",zland=5,zcontour=6.2,):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # カラーバーの範囲の指定
    if clev_min1 is not None and clev_max1 is not None and clev_int1 is not None:
        clevels1 = np.arange(clev_min1,clev_max1+clev_int1/2,clev_int1)
        cticks1 = None
    elif clev_min1 is not None and clev_max1 is not None and clev_int1 == None:
        nlev = 12
        clevels1 = np.linspace(clev_min1,clev_max1,nlev)
        cticks1 = list(clevels1[:nlev//2:2])+list(clevels1[nlev//2+1::2])
    elif (clev_min1,clev_max1,clev_int1)==(None,None,None):
        clevels1 = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks1 = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    # field2のコンターレベルの指定
    if clev_min2 is not None and clev_max2 is not None and clev_int2 is not None:
        clevels2 = np.arange(clev_min2,clev_max2+clev_int2,clev_int2)
    elif (clev_min2,clev_max2,clev_int2)==(None,None,None):
        clevels2 = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # field2の副コンター、細い線
    clev_int2_sub = clev_int2/5
    if clev_min2 is not None and clev_max2 is not None and clev_int2_sub is not None:
        clevels2_sub = np.arange(clev_min2,clev_max2+clev_int2_sub,clev_int2_sub)
    elif (clev_min2,clev_max2,clev_int2_sub)==(None,None,None):
        clevels2_sub = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # Plot
    if add_colorbar:
        c=field1.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels1,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1,"aspect":40,'ticks':cticks1},)
    else:
        c=field1.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels1,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,)
    # field2はコンター
    contour = field2.plot.contour(
        ax=ax,
        transform=ccrs.PlateCarree(),
        levels=clevels2,
        linewidths=contourwidth,
        # linestyles=['-','--','--','--','--'],
        colors=ccontour,zorder=zcontour,
    )
    # コンターのラベルの作成
    if clabel:
        ax.clabel(
            contour,
            fmt=fmt,
            fontsize=clabelsize,inline_spacing=inline_spacing,
            colors=cclabel,
            zorder=6.1
        )
    # sub_contour
    if sub_contour:
        field2.plot.contour(
            ax=ax,
            transform=ccrs.PlateCarree(),
            levels=clevels2_sub,
            linewidths=0.2,
            colors=ccontour,
            linestyles='--',
            add_labels=False,
            zorder=6
        )
    ax_addhatch(ax,field_hatch.lon.values,field_hatch.lat.values,field_hatch,
    hatches=hatches,ec=echatch)
    # 指定領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)
    
    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=10)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
        draw_labels=False,
        alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=zland)

    if cout:
        return c

def axplot_polar_field_double_hatch(ax,field1, field2, field_hatch,
                   clev_min1=None,clev_max1=None,clev_int1=None,
                   clev_min2=None,clev_max2=None,clev_int2=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",add_colorbar=False,cout=True,ccontour='black',
                   clabel=False,clabelsize='medium',cclabel="black",inline_spacing=5,grid=False,grid_width=1.,contourwidth=1,
                   sub_contour=False,hatches=[".."],echatch="black",
                   fmt='%.1f',
                   rec=False,xy=None,width=None,height=None,
                   landcol=True,landfc="beige",cland='lightgray',zland=5,zcontour=6.2,):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # カラーバーの範囲の指定
    if clev_min1 is not None and clev_max1 is not None and clev_int1 is not None:
        clevels1 = np.arange(clev_min1,clev_max1+clev_int1/2,clev_int1)
        cticks1 = None
    elif clev_min1 is not None and clev_max1 is not None and clev_int1 == None:
        nlev = 12
        clevels1 = np.linspace(clev_min1,clev_max1,nlev)
        cticks1 = list(clevels1[:nlev//2:2])+list(clevels1[nlev//2+1::2])
    elif (clev_min1,clev_max1,clev_int1)==(None,None,None):
        clevels1 = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks1 = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    # field2のコンターレベルの指定
    if clev_min2 is not None and clev_max2 is not None and clev_int2 is not None:
        clevels2 = np.arange(clev_min2,clev_max2+clev_int2,clev_int2)
    elif (clev_min2,clev_max2,clev_int2)==(None,None,None):
        clevels2 = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # field2の副コンター、細い線
    clev_int2_sub = clev_int2/5
    if clev_min2 is not None and clev_max2 is not None and clev_int2_sub is not None:
        clevels2_sub = np.arange(clev_min2,clev_max2+clev_int2_sub,clev_int2_sub)
    elif (clev_min2,clev_max2,clev_int2_sub)==(None,None,None):
        clevels2_sub = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # Plot
    if add_colorbar:
        c=field1.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels1,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1,"aspect":40,'ticks':cticks1},)
    else:
        c=field1.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels1,
        cmap=cmap,
        extend='both',
        add_colorbar=add_colorbar,)
    # field2はコンター
    contour = field2.plot.contour(
        ax=ax,
        transform=ccrs.PlateCarree(),
        levels=clevels2,
        linewidths=contourwidth,
        # linestyles=['-','--','--','--','--'],
        colors=ccontour,zorder=zcontour,
    )
    # コンターのラベルの作成
    if clabel:
        ax.clabel(
            contour,
            fmt=fmt,
            fontsize=clabelsize,inline_spacing=inline_spacing,
            colors=cclabel,
            zorder=6.1
        )
    # sub_contour
    if sub_contour:
        field2.plot.contour(
            ax=ax,
            transform=ccrs.PlateCarree(),
            levels=clevels2_sub,
            linewidths=0.2,
            colors=ccontour,
            linestyles='--',
            add_labels=False,
            zorder=6
        )
    ax_addhatch(ax,field_hatch.lon.values,field_hatch.lat.values,field_hatch,
    hatches=hatches,ec=echatch)
    # 指定領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)
    
    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    # xticks = np.arange(0,360,xtickint)
    # yticks = np.arange(-80,90,ytickint)
    # ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    # ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    # ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=10)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
        draw_labels=False,
        alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=cland,zorder=zland)

    if cout:
        return c
#
def axplot_whitemap(ax,x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   title="",grid=False,grid_width=1.,zrec=10,zland=1,
                   rec=False,xy=None,width=None,height=None,
                   landcol=True,landfc="beige",):
   
    # subarc/subtro front領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='black',linewidth=2.5,
        zorder=zrec)
        ax.add_patch(r)

    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
   
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=3)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),
                     linestyle="--",linewidth=grid_width,
                     draw_labels=False,
                     alpha=0.8,
                     zorder=2)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=zland)

def ax_addpatch(ax,xy,w,h,ec,ls='-',lw=1.5,fill=False,zorder=20):
    r=patches.Rectangle(xy=xy,width=w,height=h,
        fill=fill,edgecolor=ec,linestyle=ls,linewidth=lw,
        zorder=zorder)
    ax.add_patch(r)

def ax_xr_addhatch(ax,field,hatches=[".."],ec="black",colors="none",corner_mask=True,zorder=5,cout=False):
    plt.rcParams["hatch.color"]=ec
    chatch=field.plot.contourf(ax=ax,hatches=hatches,colors=colors,
                transform=ccrs.PlateCarree(),corner_mask=corner_mask,zorder=zorder,
                )
    if cout:
        return chatch

def ax_addhatch(ax,x,y,field,hatches=[".."],ec="black",colors="none",corner_mask=True,
                transform=ccrs.PlateCarree(),zorder=5):
    plt.rcParams["hatch.color"]=ec
    ax.contourf(x,y,field,hatches=hatches,colors=colors,
                transform=transform,zorder=zorder,corner_mask=corner_mask)

def ax_xaxis2lon(ax,xmin,xmax,xint):
    xticks = np.arange(xmin,xmax+xint,xint)
    ax.set_xticks(xticks)
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    ax.xaxis.set_major_formatter(lon_formatter)
#
def plot_laghovmuller(ax,
                   var,clev_min, clev_max, clev_int,
                   x_min=140, x_max=240,
                   lagmin=-60,lagmax=60,
                   lon='lon',lag='lag',
                   xtickint=20,
                   cmap='RdBu_r', var_label="",
                   title="",
                   savefig=False, fname_save=""):
    '''
    da: (time, lon)の構造を持つdataarray
    Purpose: Hovmuller diagramを描く
    参考: https://unidata.github.io/python-gallery/examples/Hovmoller_Diagram.html
    '''
    
    import cartopy.crs as ccrs
    from   cartopy.mpl.ticker import LongitudeFormatter,LatitudeFormatter
    
    da = var.sel(lag=slice(lagmin,lagmax))
    
    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
        cticks = None
    elif clev_min is not None and clev_max is not None and clev_int == None:
        nlev = 12
        clevels = np.linspace(clev_min,clev_max,nlev)
        cticks = list(clevels[:nlev//2:2])+list(clevels[nlev//2+1::2])#np.linspace(clev_min,clev_max,7)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    
    cf = ax.contourf(da[lon].values, da[lag].values, da.values,
                levels=clevels, cmap=cmap, extend='both'
                )
    plt.colorbar(cf, pad=0.1,
        extend='both',orientation='horizontal',shrink=1,aspect=40,
        ticks=cticks)
    
    xticks = np.arange(360//xtickint+1)*xtickint
    ax.set_xticks(xticks,)
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    ax.xaxis.set_major_formatter(lon_formatter)
    
    ax.axes.tick_params(labelsize=13)
    ## region
    ax.set_xlim([x_min,x_max])
    # fig/label title
    ax.set_xlabel("",fontsize=18)
    # ax.set_ylabel("Time",fontsize=18)
    # ax.set_title(title,fontsize=20)
    
def plot_hovmuller_double(ax,
                          var1,var2,
                          clev_min, clev_max, clev_int,
                          clev_min2, clev_max2, clev_int2,
                          lagmin=-60,lagmax=60,
                          x_min=145, x_max=210,
                          lon='lon',lag='lag',
                          xtickint=20,
                          cmap='RdBu_r', var_label="",
                          contourwidth=1,clabel=False,
                          fmt='%.1f',
                          title="",
                          savefig=False, fname_save=""):
    '''
    da: (time, lon)の構造を持つdataarray
    Purpose: Hovmuller diagramを描く
    参考: https://unidata.github.io/python-gallery/examples/Hovmoller_Diagram.html
    '''
    
    import cartopy.crs as ccrs
    from   cartopy.mpl.ticker import LongitudeFormatter,LatitudeFormatter

    
    da1 = var1.sel(lag=slice(lagmin,lagmax))
    da2 = var2.sel(lag=slice(lagmin,lagmax))
    
    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
        cticks = None
    elif clev_min is not None and clev_max is not None and clev_int == None:
        nlev = 12
        clevels = np.linspace(clev_min,clev_max,nlev)
        cticks = list(clevels[:nlev//2:2])+list(clevels[nlev//2+1::2])#np.linspace(clev_min,clev_max,7)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    # field2のコンターレベルの指定
    if clev_min2 is not None and clev_max2 is not None and clev_int2 is not None:
        clevels2 = np.arange(clev_min2,clev_max2+clev_int2,clev_int2)
    elif (clev_min2,clev_max2,clev_int2)==(None,None,None):
        clevels2 = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    
    cf = ax.contourf(da1[lon].values, da1[lag].values, da1.values,
                levels=clevels, cmap=cmap, extend='both'
                )
    plt.colorbar(cf, pad=0.1,
        extend='both',orientation='horizontal',shrink=1,aspect=40,
        ticks=cticks)
    # plot contour
    contour = ax.contour(da2[lon].values,da2[lag].values,da2.values,
               levels=clevels2,
               linewidth=contourwidth,colors='dimgray',
               alpha=0.7)
    if clabel:
        ax.clabel(
            contour,
            fmt=fmt,
            colors='black',
        )
    
    xticks = np.arange(360//xtickint+1)*xtickint
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    ax.xaxis.set_major_formatter(lon_formatter)
    
    ax.axes.tick_params(labelsize=13)
    ## region
    ax.set_xlim([x_min,x_max])
    # fig/label title
    ax.set_xlabel("",fontsize=14)
    # ax.set_ylabel("Time",fontsize=14)
    # ax.set_title(title,fontsize=20)
#   
def plot_hovmuller_hatch(ax,
                         var1,var_hatch,
                         clev_min, clev_max, clev_int,
                         x_min=140, x_max=240,
                         lon='lon',lag='lag',
                         xtickint=20,transform=None,
                         cmap='RdBu_r', ):
    '''
    da: (time, lon)の構造を持つdataarray
    Purpose: Hovmuller diagramを描く
    参考: https://unidata.github.io/python-gallery/examples/Hovmoller_Diagram.html
    '''
    
    import cartopy.crs as ccrs
    from   cartopy.mpl.ticker import LongitudeFormatter,LatitudeFormatter
    
    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
        cticks = None
    elif clev_min is not None and clev_max is not None and clev_int == None:
        nlev = 12
        clevels = np.linspace(clev_min,clev_max,nlev)
        cticks = list(clevels[:nlev//2:2])+list(clevels[nlev//2+1::2])#np.linspace(clev_min,clev_max,7)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    
    cf = ax.contourf(var1[lon].values, var1[lag].values, var1.values,
                levels=clevels, cmap=cmap, extend='both'
                )
    plt.colorbar(cf, pad=0.1,
        extend='both',orientation='horizontal',shrink=1,aspect=40,
        ticks=cticks)
    
    # hatching
    # tcval=stats.t.ppf(1-(1-alpha)/2,dof)
    # vart.plot.contourf(ax=ax,
    #             levels=[-10**5,-tcval,tcval,10**5],
    #             hatches=['..',None,'..'],
    #             add_colorbar=False,
    #             colors='none',
    #             )
    ax_addhatch(ax,var_hatch[lon],var_hatch[lag],var_hatch,transform=transform)
    
    xticks = np.arange(360//xtickint+1)*xtickint
    ax.set_xticks(xticks)
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.axes.tick_params(labelsize=13)
    ## region
    ax.set_xlim([x_min,x_max])

def plot_hovmuller_double_hatch(ax,
                          var1,var2,
                          vart,
                          clev_min, clev_max, clev_int,
                          clev_min2, clev_max2, clev_int2,
                          dof,alpha=0.95,
                          lagmin=-60,lagmax=60,
                          x_min=145, x_max=210,
                          lon='lon',lag='lag',
                          xtickint=20,
                          cmap='RdBu_r',
                          contourwidth=1,concolors='dimgray',
                          clabel=False,
                          fmt='%.1f',):
    '''
    da: (time, lon)の構造を持つdataarray
    Purpose: Hovmuller diagramを描く
    参考: https://unidata.github.io/python-gallery/examples/Hovmoller_Diagram.html
    '''

    
    da1 = var1.sel(lag=slice(lagmin,lagmax))
    da2 = var2.sel(lag=slice(lagmin,lagmax))
    dat = vart.sel(lag=slice(lagmin,lagmax))
    
    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
        cticks = None
    elif clev_min is not None and clev_max is not None and clev_int == None:
        nlev = 12
        clevels = np.linspace(clev_min,clev_max,nlev)
        cticks = list(clevels[:nlev//2:2])+list(clevels[nlev//2+1::2])#np.linspace(clev_min,clev_max,7)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    # field2のコンターレベルの指定
    if clev_min2 is not None and clev_max2 is not None and clev_int2 is not None:
        clevels2 = np.arange(clev_min2,clev_max2+clev_int2,clev_int2)
    elif (clev_min2,clev_max2,clev_int2)==(None,None,None):
        clevels2 = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    
    cf = ax.contourf(da1[lon].values, da1[lag].values, da1.values,
                levels=clevels, cmap=cmap, extend='both'
                )
    plt.colorbar(cf, pad=0.1,
        extend='both',orientation='horizontal',shrink=1,aspect=40,
        ticks=cticks)
    # plot contour
    contour = ax.contour(da2[lon].values,da2[lag].values,da2.values,
               levels=clevels2,
               linewidth=contourwidth,colors=concolors,
               alpha=0.7)
    # hatching
    tcval=stats.t.ppf(1-(1-alpha)/2,dof)
    dat.plot.contourf(ax=ax,
                levels=[-10**5,-tcval,tcval,10**5],
                hatches=['..',None,'..'],
                add_colorbar=False,
                colors='none',
                )
    
    if clabel:
        ax.clabel(
            contour,
            fmt=fmt,
            colors='black',
        )
    
    xticks = np.arange(360//xtickint+1)*xtickint
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    ax.xaxis.set_major_formatter(lon_formatter)
    
    ax.axes.tick_params(labelsize=13)
    ## region
    ax.set_xlim([x_min,x_max])

def draw_hrz_field_double(field1, field2,
                   clev_min1=None,clev_max1=None,clev_int1=None,
                   clev_min2=None,clev_max2=None,clev_int2=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",
                   clabel=False,grid=False,grid_width=1.,contourwidth=1,
                   sub_contour=False,
                   fmt='%.1f',
                   rec=False,xy=None,width=None,height=None,
                   landcol=True,landfc="beige",zorder_land=5,z_contour=6.2,
                   savefig=False,fname_save=None):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # Figure/Axes objects
    fig = plt.figure(figsize=(6,4),dpi=150,layout='constrained') # 図のサイズと解像度を指定
    ax = fig.add_subplot(projection=ccrs.PlateCarree(central_longitude=180)) # cartopyのprojectionを指定したAxesオブジェクトを生成

    # カラーバーの範囲の指定
    if clev_min1 is not None and clev_max1 is not None and clev_int1 is not None:
        clevels1 = np.arange(clev_min1,clev_max1+clev_int1/2,clev_int1)
        cticks1 = None
    elif clev_min1 is not None and clev_max1 is not None and clev_int1 == None:
        nlev = 12
        clevels1 = np.linspace(clev_min1,clev_max1,nlev)
        cticks1 = list(clevels1[:nlev//2:2])+list(clevels1[nlev//2+1::2])
    elif (clev_min1,clev_max1,clev_int1)==(None,None,None):
        clevels1 = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks1 = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    # field2のコンターレベルの指定
    if clev_min2 is not None and clev_max2 is not None and clev_int2 is not None:
        clevels2 = np.arange(clev_min2,clev_max2+clev_int2,clev_int2)
    elif (clev_min2,clev_max2,clev_int2)==(None,None,None):
        clevels2 = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # field2の副コンター、細い線
    clev_int2_sub = clev_int2/5
    if clev_min2 is not None and clev_max2 is not None and clev_int2_sub is not None:
        clevels2_sub = np.arange(clev_min2,clev_max2+clev_int2_sub,clev_int2_sub)
    elif (clev_min2,clev_max2,clev_int2_sub)==(None,None,None):
        clevels2_sub = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # Plot
    # field1は塗りつぶし
    # field2はコンター
    field1.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels1,
        cmap=cmap,
        extend='both',
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1.,"aspect":40,'ticks':cticks1},
    ) # xarrayに内蔵されたplot.contourfメソッド。
    contour = field2.plot.contour(
        ax=ax,
        transform=ccrs.PlateCarree(),
        levels=clevels2,
        linewidths=contourwidth,
        # linestyles=['-','--','--','--','--'],
        colors='black',zorder=z_contour,
    )
    # コンターのラベルの作成
    if clabel:
        ax.clabel(
            contour,
            fmt=fmt,
            fontsize=6,
            colors='black',
            zorder=6.1
        )
    # sub_contour
    if sub_contour:
        field2.plot.contour(
            ax=ax,
            transform=ccrs.PlateCarree(),
            levels=clevels2_sub,
            linewidths=0.2,
            colors='black',
            linestyles='--',
            add_labels=False,
            zorder=6
        )
    
    # 指定領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)
    
    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=10)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
        draw_labels=False,
        alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=zorder_land)
    # save figure
    if savefig: 
        fig.savefig(fname_save)

def draw_hrz_field_double_hatch(field1,field2,field_hatch,tc_val,
                   clev_min1=None,clev_max1=None,clev_int1=None,
                   clev_min2=None,clev_max2=None,clev_int2=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",
                   grid=False,grid_width=1,
                   clabel=False,
                   sub_contour=False,
                   rec=False,
                   xy=None,width=None,height=None,
                   fmt='%.1f',
                   landcol=True,landfc="beige",z_land=3,z_contour=4,z_hatch=2,
                   savefig=False,fname_save=None):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # Figure/Axes objects
    fig = plt.figure(figsize=(6,4),dpi=150,layout='constrained') # 図のサイズと解像度を指定
    ax = fig.add_subplot(projection=ccrs.PlateCarree(central_longitude=180)) # cartopyのprojectionを指定したAxesオブジェクトを生成

   # カラーバーの範囲の指定
    if clev_min1 is not None and clev_max1 is not None and clev_int1 is not None:
        clevels1 = np.arange(clev_min1,clev_max1+clev_int1/2,clev_int1)
        cticks1 = None
    elif clev_min1 is not None and clev_max1 is not None and clev_int1 == None:
        nlev = 12
        clevels1 = np.linspace(clev_min1,clev_max1,nlev)
        cticks1 = list(clevels1[:nlev//2:2])+list(clevels1[nlev//2+1::2])
    elif (clev_min1,clev_max1,clev_int1)==(None,None,None):
        clevels1 = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks1 = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    # field2のコンターレベルの指定
    if clev_min2 is not None and clev_max2 is not None and clev_int2 is not None:
        clevels2 = np.arange(clev_min2,clev_max2+clev_int2,clev_int2)
    elif (clev_min2,clev_max2,clev_int2)==(None,None,None):
        clevels2 = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # field2の副コンター、細い線
    clev_int2_sub = clev_int2/5
    if clev_min2 is not None and clev_max2 is not None and clev_int2_sub is not None:
        clevels2_sub = np.arange(clev_min2,clev_max2+clev_int2_sub,clev_int2_sub)
    elif (clev_min2,clev_max2,clev_int2_sub)==(None,None,None):
        clevels2_sub = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # Plot
    # field1は塗りつぶし
    # field2はコンター
    field1.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels1,
        cmap=cmap,
        extend='both',
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1.,"aspect":40,'ticks':cticks1},
    ) # xarrayに内蔵されたplot.contourfメソッド。
    contour = field2.plot.contour(
        ax=ax,
        transform=ccrs.PlateCarree(),
        levels=clevels2,
        linewidths=1,
        zorder=z_contour,
        # linestyles=['-','--','--','--','--'],
        colors='black'
    )
    # hatching
    field_hatch.plot.contourf(ax=ax,
                levels=[-200,-tc_val,tc_val,200],
                hatches=['..',None,'..'],
                add_colorbar=False,
                colors='none',zorder=z_hatch,transform=ccrs.PlateCarree()
                )
    # コンターのラベルの作成
    if clabel:
        ax.clabel(
            contour,
            fmt=fmt,
            fontsize=6,
            colors='black',
        )
    # sub_contour
    if sub_contour:
        field2.plot.contour(
            ax=ax,
            transform=ccrs.PlateCarree(),
            levels=clevels2_sub,
            linewidths=0.2,
            colors='black',
            linestyles='--',
            add_labels=False,
        )
    # subarc/subtro front領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)
    
    
    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=10)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
        draw_labels=False,
        alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=z_land)
    # save figure
    if savefig: 
        fig.savefig(fname_save)

def draw_hrz_field_double_hatch_hrz(field1,field2,field_hatch,tcval_da,
                   clev_min1=None,clev_max1=None,clev_int1=None,
                   clev_min2=None,clev_max2=None,clev_int2=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",
                   grid=False,grid_width=1,
                   clabel=False,
                   sub_contour=False,
                   rec=False,
                   xy=None,width=None,height=None,
                   fmt='%.1f',
                   landcol=True,landfc="beige",z_land=3,z_contour=4,z_hatch=2,
                   savefig=False,fname_save=None):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # Figure/Axes objects
    fig = plt.figure(figsize=(6,4),dpi=150,layout='constrained') # 図のサイズと解像度を指定
    ax = fig.add_subplot(projection=ccrs.PlateCarree(central_longitude=180)) # cartopyのprojectionを指定したAxesオブジェクトを生成

   # カラーバーの範囲の指定
    if clev_min1 is not None and clev_max1 is not None and clev_int1 is not None:
        clevels1 = np.arange(clev_min1,clev_max1+clev_int1/2,clev_int1)
        cticks1 = None
    elif clev_min1 is not None and clev_max1 is not None and clev_int1 == None:
        nlev = 12
        clevels1 = np.linspace(clev_min1,clev_max1,nlev)
        cticks1 = list(clevels1[:nlev//2:2])+list(clevels1[nlev//2+1::2])
    elif (clev_min1,clev_max1,clev_int1)==(None,None,None):
        clevels1 = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks1 = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    # field2のコンターレベルの指定
    if clev_min2 is not None and clev_max2 is not None and clev_int2 is not None:
        clevels2 = np.arange(clev_min2,clev_max2+clev_int2,clev_int2)
    elif (clev_min2,clev_max2,clev_int2)==(None,None,None):
        clevels2 = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # field2の副コンター、細い線
    clev_int2_sub = clev_int2/5
    if clev_min2 is not None and clev_max2 is not None and clev_int2_sub is not None:
        clevels2_sub = np.arange(clev_min2,clev_max2+clev_int2_sub,clev_int2_sub)
    elif (clev_min2,clev_max2,clev_int2_sub)==(None,None,None):
        clevels2_sub = 9 
    else:
        raise Exception("Contour level max/min/int is not correct!")
    # Plot
    # field1は塗りつぶし
    # field2はコンター
    field1.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels1,
        cmap=cmap,
        extend='both',
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1.,"aspect":40,'ticks':cticks1},
    ) # xarrayに内蔵されたplot.contourfメソッド。
    contour = field2.plot.contour(
        ax=ax,
        transform=ccrs.PlateCarree(),
        levels=clevels2,
        linewidths=1,
        zorder=z_contour,
        # linestyles=['-','--','--','--','--'],
        colors='black'
    )
    # hatching
    (np.abs(field_hatch)>tcval_da).astype(int)\
        .plot.contourf(ax=ax,
                       levels = [0,.999999,1000],
                       hatches=[None,'..'],
                       add_colorbar=False,
                       colors='none',
                       zorder=z_hatch,transform=ccrs.PlateCarree()
                      )
    # コンターのラベルの作成
    if clabel:
        ax.clabel(
            contour,
            fmt=fmt,
            fontsize=6,
            colors='black',
        )
    # sub_contour
    if sub_contour:
        field2.plot.contour(
            ax=ax,
            transform=ccrs.PlateCarree(),
            levels=clevels2_sub,
            linewidths=0.2,
            colors='black',
            linestyles='--',
            add_labels=False,
        )
    # subarc/subtro front領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)
    
    
    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=10)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
        draw_labels=False,
        alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=z_land)
    # save figure
    if savefig: 
        fig.savefig(fname_save)

def draw_hrz_field_contour(field,
                   clev_min=None,clev_max=None,clev_int=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   fmt='%.1f',
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   contourwidth=0.5,
                   subarc=False,subtro=False,
                   landcol=True,landfc="beige",z_land=4.9,
                   savefig=False,fname_save=None):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # Figure/Axes objects
    fig = plt.figure(figsize=(6,4),dpi=150,layout='constrained') # 図のサイズと解像度を指定
    ax = fig.add_subplot(projection=ccrs.PlateCarree(central_longitude=180)) # cartopyのprojectionを指定したAxesオブジェクトを生成

    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 19 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
    else:
        raise Exception("Color level max/min/int is not correct!")
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # contour

    plot = field.plot.contour(
        ax=ax,
        transform=ccrs.PlateCarree(),
        levels=clevels,
        colors='black',
        linewidths=contourwidth,
        zorder=5
    )
    # コンターのラベルの作成
    ax.clabel(
        plot,
        fmt=fmt,
        fontsize=6,
        colors='black',
        zorder=6.1,
        inline_spacing=7
    )
    # とか，
    # plot = ax.plot.contour(
    #     field["lon"],
    #     field["lat"],
    #     field.values,
    #     transform=ccrs.PlateCaree(),
    # )
    # で描けると思います。
    
    # subarc/subtro front領域を四角形で囲う
    if subarc:
        r=patches.Rectangle(xy=(-30,34),width=30,height=14,
        fill=False,edgecolor='black',linewidth=1.5,
        zorder=20)
        ax.add_patch(r)
    elif subtro:
        r=patches.Rectangle(xy=(0,22),width=30,height=14,
        fill=False,edgecolor='black',linewidth=1.5,
        zorder=20)
        ax.add_patch(r)
    

    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=10)
    #ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
    # draw_labels=False,
    # alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=z_land)
    # save figure
    if savefig: 
        fig.savefig(fname_save)

def draw_hrz_field_hatch(field,field_hatch,tc_val,
                   clev_min=None,clev_max=None,clev_int=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",
                   contour=False,
                   rec=False,
                   xy=None,width=None,height=None,
                   landcol=True,landfc="beige",
                   savefig=False,fname_save=None):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # Figure/Axes objects
    fig = plt.figure(figsize=(6,4),dpi=150,layout='constrained') # 図のサイズと解像度を指定
    ax = fig.add_subplot(projection=ccrs.PlateCarree(central_longitude=180)) # cartopyのprojectionを指定したAxesオブジェクトを生成

    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
        cticks = None
    elif clev_min is not None and clev_max is not None and clev_int == None:
        nlev = 12
        clevels = np.linspace(clev_min,clev_max,nlev)
        cticks = list(clevels[:nlev//2:2])+list(clevels[nlev//2+1::2])#np.linspace(clev_min,clev_max,7)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks = None
    else:
        raise Exception("Color level max/min/int is not correct!")
    # Plot
    field.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels,
        cmap=cmap,
        extend='both',
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1.,"aspect":40,'ticks':cticks},
    ) # xarrayに内蔵されたplot.contourfメソッド。
    
    # hatching
    field_hatch.plot.contourf(ax=ax,
                levels=[-200,-tc_val,tc_val,200],
                hatches=['..',None,'..'],
                add_colorbar=False,
                colors='none',zorder=10,transform=ccrs.PlateCarree()
                )

    # subarc/subtro front領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=1.5,
        zorder=20)
        ax.add_patch(r)
    

    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=13)
    #ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
    # draw_labels=False,
    # alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=12)
    # save figure
    if savefig: 
        fig.savefig(fname_save)

def draw_hrz_field_hatch_hrz(field,field_hatch,tcval_da,
                   clev_min=None,clev_max=None,clev_int=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   cmap="RdBu_r",
                   grid=False,grid_width=1,
                   clabel=False,
                   sub_contour=False,
                   rec=False,
                   xy=None,width=None,height=None,
                   fmt='%.1f',
                   landcol=True,landfc="beige",z_land=3,z_contour=4,z_hatch=2,
                   savefig=False,fname_save=None):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # Figure/Axes objects
    fig = plt.figure(figsize=(6,4),dpi=150,layout='constrained') # 図のサイズと解像度を指定
    ax = fig.add_subplot(projection=ccrs.PlateCarree(central_longitude=180)) # cartopyのprojectionを指定したAxesオブジェクトを生成

   # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
        cticks = None
    elif clev_min is not None and clev_max is not None and clev_int == None:
        nlev = 12
        clevels = np.linspace(clev_min,clev_max,nlev)
        cticks = list(clevels[:nlev//2:2])+list(clevels[nlev//2+1::2])
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 9 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
        cticks = None
    else:
        raise Exception("Color level max/min/int is not correct!")

    # Plot
    # fieldは塗りつぶし
    # field2はコンター
    field.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        center=0,
        levels=clevels,
        cmap=cmap,
        extend='both',
        cbar_kwargs={"label":var_label,"orientation":"horizontal",
                     "shrink":1.,"aspect":40,'ticks':cticks},
    ) # xarrayに内蔵されたplot.contourfメソッド。
    
    # hatching
    (np.abs(field_hatch)>tcval_da).astype(int)\
        .plot.contourf(ax=ax,
                       levels = [0,.999999,1000],
                       hatches=[None,'..'],
                       add_colorbar=False,
                       colors='none',
                       zorder=z_hatch,transform=ccrs.PlateCarree()
                      )
    
    # subarc/subtro front領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=2.5,
        zorder=20)
        ax.add_patch(r)
    
    
    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=10)
    if grid:
        ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
        draw_labels=False,
        alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=z_land)
    # save figure
    if savefig: 
        fig.savefig(fname_save)

def draw_hrz_field_contour_hatch(field,field_hatch,tc_val,
                   clev_min=None,clev_max=None,clev_int=None,
                   x_min=120,x_max=260,y_min=-20,y_max=70,
                   fmt='%.1f',
                   xtickint=20,ytickint=10,
                   var_label="",title="",
                   rec=False,
                   xy=None,width=None,height=None,
                   landcol=True,landfc="beige",
                   savefig=False,fname_save=None):
    """
    field     : xr.DataArray , 2-dims. horizontal data array
    var_label : string       , discripsion of the variable
    title     : string       , title of the Figure
    ------------------------------------------------------------
    水平方向2次元のxarrayの配列を受け取り，描画する関数。
    2つの軸の名前が("lon","lat")になっていることを想定しています。
    """

    # Figure/Axes objects
    fig = plt.figure(figsize=(6,4),dpi=150,layout='constrained') # 図のサイズと解像度を指定
    ax = fig.add_subplot(projection=ccrs.PlateCarree(central_longitude=180)) # cartopyのprojectionを指定したAxesオブジェクトを生成

    # カラーバーの範囲の指定
    if clev_min is not None and clev_max is not None and clev_int is not None:
        clevels = np.arange(clev_min,clev_max+clev_int/2,clev_int)
    elif (clev_min,clev_max,clev_int)==(None,None,None):
        clevels = 19 # カラーバーを特に指定しなければ，9つのレベルに分かれて色付けをする
    else:
        raise Exception("Color level max/min/int is not correct!")
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # contour

    plot = field.plot.contour(
        ax=ax,
        transform=ccrs.PlateCarree(),
        levels=clevels,
        colors='black',
        linewidths=0.5,
        zorder=5
    )
    # コンターのラベルの作成
    ax.clabel(
        plot,
        fmt=fmt,
        fontsize=6,
        colors='black',
        zorder=6.1,
        inline_spacing=7
    )

    # hatching
    field_hatch.plot.contourf(ax=ax,
                levels=[-200,-tc_val,tc_val,200],
                hatches=['..',None,'..'],
                add_colorbar=False,
                colors='none',zorder=10,transform=ccrs.PlateCarree()
                )
    # subarc/subtro front領域を四角形で囲う
    if rec:
        r=patches.Rectangle(xy=xy,width=width,height=height,
        fill=False,edgecolor='dimgrey',linestyle='--',linewidth=1.5,
        zorder=20)
        ax.add_patch(r)
    

    # Ticks # この辺は，最初の頃はおまじないだと思っておけば良いと思います。
    xticks = np.arange(0,360,xtickint)
    yticks = np.arange(-80,90,ytickint)
    ax.set_xticks(xticks,crs=ccrs.PlateCarree())
    ax.set_yticks(yticks,crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ax.tick_params('x')
    # ax.tick_params('y')

    # fig/label title
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title)
    
    ## region
    ax.set_extent([x_min,x_max,y_min,y_max],crs=ccrs.PlateCarree())
    # 海岸線とグリッドラインの描画
    ax.coastlines(resolution="50m",linewidth=0.5,zorder=6)
    #ax.gridlines(crs=ccrs.PlateCarree(),linestyle="--",linewidth=grid_width,
    # draw_labels=False,
    # alpha=0.8,zorder=10)
    #大陸部分の塗りつぶし
    if landcol:
        import cartopy.feature as cfea
        ax.add_feature(cfea.LAND.with_scale("50m"),fc=landfc,zorder=4.9)
    # save figure
    if savefig: 
        fig.savefig(fname_save)
#
def plot_contourf(ax,x,y,var,
                  cmin=0.,cmax=1.,cint=0.1,
                  extend='both',
                  title=None,
                  xlabel=None,ylabel=None,
                  cmap='viridis',
                  pad = 0.1,):
    clevels = np.arange(cmin,cmax+cint,cint)
    cticks = None
    xm,ym = np.meshgrid(x,y)
    cf = ax.contourf(xm,ym,var,
                        levels=clevels,cmap=cmap,extend=extend)
    plt.colorbar(cf, pad=pad,
            extend=extend,orientation='horizontal',shrink=1,aspect=40,
            ticks=cticks)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

def plot_contour(ax,x,y,var,
                  cmin=0.,cmax=1.,cint=0.1,
                  linewidths=2,colors='black',
                  title=None,
                  xlabel=None,ylabel=None,
                  clabel=False,fmt=None,
                  ):
    clevels = np.arange(cmin,cmax+cint,cint)
    cticks = None

    contour = ax.contour(x,y,var,
                    levels=clevels,linewidths=linewidths,
                    colors=colors)
    if clabel:
        ax.clabel(
            contour,
            fmt=fmt,
            fontsize=6,
            colors='black',
            zorder=6.1
        )

def plot_pcolormesh(ax,x,y,var,
                  cmin=0.,cmax=1.,cint=0.1,
                  extend='both',
                  title=None,
                  xlabel=None,ylabel=None,
                  cmap='viridis',
                  pad = 0.1,):
    clevels = np.arange(cmin,cmax+cint,cint)
    cticks = None

    cf = ax.pcolormesh(x,y,var,
                       vmin=cmin,vmax=cmax,
                        cmap=cmap)
    plt.colorbar(cf, pad=pad,
            extend=extend,orientation='horizontal',shrink=1,aspect=40,
            ticks=cticks)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
def pcolmesh_lonlon(fig,ax,c,x,y,
                    xmin=140,xmax=240,dx=1,
                    ymin=140,ymax=240,dy=1,
                    vmin=None,vmax=None,
                    xlabel='Longitude',ylabel='Longitude',
                    cmap='coolwarm',
                    title=None,
                    savefig=False,fname=None):
    ax.invert_yaxis()
    # Make a copy
    cmap = plt.cm.get_cmap(cmap).copy()
    # Choose the color
    cmap.set_bad('silver',1.)
    
    # x = np.arange(xmin-dx*0.5,xmax+dx*0.5,dx)
    # y = np.arange(ymin-dy*0.5,ymax+dy*0.5,dy)
    pcolmesh = ax.pcolormesh(x,y,c,
                cmap=cmap,vmin=vmin,vmax=vmax
                )
    
    cbar = fig.colorbar(pcolmesh,ax=ax,)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    # ticks
    xticks = np.arange(xmin,xmax+20,20)
    yticks = np.arange(ymin,ymax+20,20)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lon_formatter)
    
    if savefig:
        fig.savefig(fname)

def cmap_white_in_mid(cmap,wmin=0.45,wmax=0.55):
    cmap_obj = plt.cm.get_cmap(cmap)
    colors = [(cmap_obj(i)) if (i < wmin or i > wmax) else (1, 1, 1, 1) for i in np.linspace(0, 1, 256)]
    custom_cmap = LinearSegmentedColormap.from_list('custom_RdBu_r', colors)

def cmaps_ipcc(cmname='slev_div'):
    import matplotlib.colors as mcolors
    cmap_txt = np.loadtxt(f'/Users/tamurayukito/ANALYSIS/Data/colormaps-master/continuous_colormaps_rgb_0-1/{cmname}.txt')
    return mcolors.LinearSegmentedColormap.from_list('colormap',cmap_txt)
