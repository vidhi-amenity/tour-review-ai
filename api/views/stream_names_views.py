from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.serializers import StreamNamesSerializer
from api.models import StreamNames
from django.db import transaction

class StreamNameViewSet(viewsets.ModelViewSet):
    queryset = StreamNames.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = StreamNamesSerializer
    pagination_class = None

    def get_queryset(self):
        return StreamNames.objects.all()

    def list(self, request, *args, **kwargs):
        stream_name_list = StreamNames.objects.all()
        serializer = StreamNamesSerializer(stream_name_list, many=True)
        return Response(data={"result": serializer.data}, status=200)

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")

        if StreamNames.objects.filter(name=name).exists():
             return Response(status=400, data={"Error": "Already Exsist"})
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        instance = self.perform_create(serializer)
        instance.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
      
    def perform_create(self, serializer):
        return serializer.save()
    
    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)

    # def perform_destroy(self, instance):
    #     instance.delete()
from rest_framework.views import APIView

class StreamNamesUpdateViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        update_data_list = request.data.get("update_results", [])

        instances_to_update = [StreamNames(id=item["id"], name=item["name"]) for item in update_data_list]
        try:
            with transaction.atomic():
                # Update the records in one shot using bulk_update
                StreamNames.objects.bulk_update(instances_to_update, ["name"])
            return Response(data={"message": "Records updated successfully."}, status=200)
        except Exception as e:
            return Response(data={"Error": str(e)}, status=500)   

